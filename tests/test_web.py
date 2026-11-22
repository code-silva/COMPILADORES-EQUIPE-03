"""Integração HTTP da interface local e eventos do pipeline compartilhado."""

import json
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from threading import Thread

import pytest

from src.cli import compile_source
from src.web import CompilerHandler, MAX_SOURCE_BYTES


@pytest.fixture
def server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), CompilerHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()
    thread.join()


def request(server, method, path, body=None, headers=None):
    connection = HTTPConnection(*server.server_address, timeout=5)
    try:
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        return response.status, response.getheader("Content-Type"), response.read()
    finally:
        connection.close()


def compile_request(server, source, filename="teste.py"):
    status, content_type, body = request(
        server, "POST", "/api/compile",
        json.dumps({"filename": filename, "source": source}),
        {"Content-Type": "application/json"},
    )
    return status, content_type, body


@pytest.mark.parametrize("path,content_type", [
    ("/", "text/html"), ("/app.js", "text/javascript"), ("/app.css", "text/css"),
])
def test_serves_interface_assets(server, path, content_type):
    status, actual_type, body = request(server, "GET", path)
    assert status == 200
    assert actual_type.startswith(content_type)
    assert body


def test_upload_generates_download_content_and_ordered_stage_events(server):
    source = "x = 42\n"
    status, content_type, body = compile_request(server, source)
    events = [json.loads(line) for line in body.splitlines()]
    assert status == 200
    assert content_type.startswith("application/x-ndjson")
    assert events[0] == {"stage": "upload", "status": "done"}
    assert [(event["stage"], event["status"]) for event in events[1:-1]] == [
        (stage, state)
        for stage in ("lexer", "parser", "semantic", "codegen")
        for state in ("running", "done")
    ]
    assert events[-1] == {
        "status": "complete", "filename": "Main.java", "java": compile_source(source),
    }


@pytest.mark.parametrize("source,stage", [
    ("x = @\n", "lexer"),
    ("if True\n    x = 1\n", "parser"),
    ("x = desconhecida\n", "semantic"),
])
def test_failure_identifies_stage_and_never_returns_java(server, source, stage):
    status, _, body = compile_request(server, source)
    events = [json.loads(line) for line in body.splitlines()]
    assert status == 200
    assert events[-1]["stage"] == stage
    assert events[-1]["status"] == "error"
    assert "Linha 1" in events[-1]["message"]
    assert not any("java" in event for event in events)
    assert not any(event["stage"] == "codegen" for event in events)


@pytest.mark.parametrize("filename,source", [
    ("teste.txt", "x = 1\n"), ("teste.py", None),
    ("teste.py", "a" * (MAX_SOURCE_BYTES + 1)),
])
def test_invalid_upload_returns_friendly_error(server, filename, source):
    status, _, body = compile_request(server, source, filename)
    assert status == 400
    assert json.loads(body)["error"]


def test_malformed_json_is_rejected(server):
    status, _, _ = request(server, "POST", "/api/compile", "{")
    assert status == 400


def test_external_origin_is_rejected(server):
    status, _, _ = request(server, "POST", "/api/compile", "{}", {"Origin": "https://example.com"})
    assert status == 403


def test_only_public_assets_can_be_read(server):
    status, _, _ = request(server, "GET", "/../cli.py")
    assert status == 404


def test_empty_python_file_can_be_converted(server):
    status, _, body = compile_request(server, "")
    assert status == 200
    result = json.loads(body.splitlines()[-1])
    assert result["status"] == "complete"
    assert "public class Main" in result["java"]
