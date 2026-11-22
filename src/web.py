"""Interface web local do compilador PyToJava. Execute com ``python -m src.web``."""

from __future__ import annotations

import argparse
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from typing import Sequence
from urllib.parse import urlsplit

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.cli import compile_source
from src.lexer import LexicalError
from src.parser import ParserError
from src.semantic import SemanticError

MAX_SOURCE_BYTES = 1024 * 1024
STATIC_DIR = Path(__file__).with_name("static")
EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"

ASSETS: dict[str, tuple[str, str]] = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
}

SECURITY_HEADERS: tuple[tuple[str, str], ...] = (
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
)


@lru_cache(maxsize=len(ASSETS))
def _load_asset(filename: str) -> bytes:
    """Carrega um asset estático em memória para evitar I/O repetido por requisição."""
    return (STATIC_DIR / filename).read_bytes()


def _list_examples() -> list[dict[str, str]]:
    """Retorna os scripts ``.py`` disponíveis na pasta ``examples/`` ordenados por nome."""
    if not EXAMPLES_DIR.is_dir():
        return []
    examples: list[dict[str, str]] = []
    for path in sorted(EXAMPLES_DIR.glob("*.py")):
        if not path.is_file():
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        examples.append({"name": path.name, "source": source})
    return examples


class CompilerHandler(BaseHTTPRequestHandler):
    """Serve a interface web e transmite eventos reais da compilação em NDJSON."""

    def _send_security_headers(self) -> None:
        for header, value in SECURITY_HEADERS:
            self.send_header(header, value)

    def _send_bytes(
        self,
        status: int,
        content_type: str,
        body: bytes,
        *,
        head_only: bool = False,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self._send_security_headers()
        self.end_headers()
        if not head_only:
            self.wfile.write(body)

    def _send_json(self, status: int, payload: dict, *, head_only: bool = False) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(
            status,
            "application/json; charset=utf-8",
            body,
            head_only=head_only,
        )

    def _handle_read_request(self, *, head_only: bool) -> None:
        route = urlsplit(self.path).path
        if route == "/api/examples":
            self._send_json(200, {"examples": _list_examples()}, head_only=head_only)
            return

        asset = ASSETS.get(route)
        if asset is None:
            self.send_error(404)
            return
        filename, content_type = asset
        body = _load_asset(filename)
        self._send_bytes(200, content_type, body, head_only=head_only)

    def do_GET(self) -> None:
        self._handle_read_request(head_only=False)

    def do_HEAD(self) -> None:
        self._handle_read_request(head_only=True)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/compile":
            self.send_error(404)
            return

        # Requisições da interface são de mesma origem. Não permitir envios
        # iniciados por páginas externas para este serviço local.
        origin = self.headers.get("Origin")
        host = self.headers.get("Host")
        if origin and (not host or origin != f"http://{host}"):
            self.send_error(403, "Origem nao permitida")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(400, "Tamanho invalido")
            return

        # JSON pode representar cada byte de controle como seis caracteres.
        if not 0 < length <= MAX_SOURCE_BYTES * 6 + 65536:
            self.send_error(413, "Arquivo muito grande ou requisicao vazia")
            return

        try:
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                raise ValueError("Envie um arquivo Python.")
            filename = payload.get("filename")
            source = payload.get("source")
            if not isinstance(filename, str) or not filename.lower().endswith(".py"):
                raise ValueError("Selecione um arquivo com extensão .py.")
            if not isinstance(source, str):
                raise ValueError("O conteúdo do arquivo deve ser texto UTF-8.")
            if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
                raise ValueError("O arquivo deve ter no máximo 1 MB.")
        except (ValueError, UnicodeError) as exc:
            self._send_json(400, {"error": str(exc)})
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self._send_security_headers()
        self.end_headers()
        current_stage = "upload"

        def emit(event: dict) -> None:
            self.wfile.write((json.dumps(event, ensure_ascii=False) + "\n").encode("utf-8"))
            self.wfile.flush()

        def progress(stage: str, status: str) -> None:
            nonlocal current_stage
            current_stage = stage
            emit({"stage": stage, "status": status})

        try:
            progress("upload", "done")
            java = compile_source(source, on_stage=progress)
            emit({"status": "complete", "filename": "Main.java", "java": java})
        except (BrokenPipeError, ConnectionResetError):
            return
        except (LexicalError, ParserError, SemanticError) as exc:
            emit({"stage": current_stage, "status": "error", "message": str(exc)})
        except Exception:
            emit({
                "stage": current_stage,
                "status": "error",
                "message": "Não foi possível concluir a conversão deste arquivo.",
            })


def build_arg_parser() -> argparse.ArgumentParser:
    """Constrói e retorna o gerenciador de argumentos da interface web local."""
    parser = argparse.ArgumentParser(
        prog="pytojava-web",
        description="Interface web local do compilador PyToJava.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta local do servidor HTTP (padrão: 8000).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Endereço de escuta local (padrão: 127.0.0.1).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Inicia o servidor HTTP local da interface web do PyToJava."""
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        server = ThreadingHTTPServer((args.host, args.port), CompilerHandler)
    except OSError as exc:
        parser.exit(
            1,
            f"Não foi possível iniciar o servidor: {exc}\n"
            f"Tente outra porta com --port {args.port + 1}.\n",
        )
    display_host = "localhost" if args.host == "127.0.0.1" else args.host
    print(f"PyToJava disponível em http://{display_host}:{args.port}", flush=True)
    print("Abra esse endereço no navegador. Para encerrar, pressione Ctrl+C.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
