"""Interface web local. Execute com ``python -m src.web``."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from src.cli import compile_source
from src.lexer import LexicalError
from src.parser import ParserError
from src.semantic import SemanticError

MAX_SOURCE_BYTES = 1024 * 1024
STATIC_DIR = Path(__file__).with_name("static")
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/app.css": ("app.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


class CompilerHandler(BaseHTTPRequestHandler):
    """Serve a página e transmite eventos reais da compilação em NDJSON."""

    def do_GET(self) -> None:
        asset = ASSETS.get(self.path)
        if asset is None:
            self.send_error(404)
            return
        filename, content_type = asset
        body = (STATIC_DIR / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/api/compile":
            self.send_error(404)
            return
        # Requisições da interface são de mesma origem. Não permitir uploads
        # iniciados por páginas externas para este serviço local.
        origin = self.headers.get("Origin")
        if origin and origin != f"http://{self.headers.get('Host')}":
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
            body = json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
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
            emit({"stage": current_stage, "status": "error",
                  "message": "Não foi possível concluir a conversão deste arquivo."})


def main() -> None:
    parser = argparse.ArgumentParser(description="Interface web local do PyToJava")
    parser.add_argument("--port", type=int, default=8000, help="Porta local (padrão: 8000)")
    args = parser.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), CompilerHandler)
    except OSError as exc:
        parser.exit(1, f"Não foi possível iniciar o servidor: {exc}\nTente outra porta com --port 8001.\n")
    print(f"PyToJava disponível em http://localhost:{args.port}", flush=True)
    print("Abra esse endereço no Chrome. Para encerrar, pressione Ctrl+C.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
