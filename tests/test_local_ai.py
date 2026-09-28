"""
Pruebas unitarias para el módulo de IA Local Autónoma (local_ai.py).
"""

import local_ai


def test_detect_available_llm():
    status = local_ai.detect_available_llm()
    assert "status" in status
    assert "type" in status
    assert "name" in status


def test_get_ollama_models(monkeypatch):
    class FakeResponse:
        status = 200
        def read(self):
            import json
            return json.dumps({
                "models": [
                    {"name": "llama3.2:latest"},
                    {"name": "qwen2.5-coder:7b"},
                    {"name": "mistral:latest"}
                ]
            }).encode("utf-8")
        def __enter__(self):
            return self
        def __exit__(self, *a):
            pass

    import urllib.request
    monkeypatch.setattr(urllib.request, "urlopen", lambda req, timeout=1.0: FakeResponse())
    monkeypatch.setattr(local_ai, "check_http_endpoint", lambda url, timeout=0.5: "11434" in url)

    models = local_ai.get_ollama_models()
    assert models == ["llama3.2:latest", "qwen2.5-coder:7b", "mistral:latest"]


def test_get_runner_download_url():
    """Verifica que get_runner_download_url retorna una URL válida con terminación .zip."""
    url = local_ai.get_runner_download_url()
    assert url.startswith("https://")
    assert url.endswith(".zip")
    assert "llama" in url.lower()


def test_download_and_extract_runner(tmp_path, monkeypatch):
    """Verifica la descarga, descompresión del ZIP en el directorio destino y limpieza del archivo temporal."""
    import zipfile
    import io

    # Crear un ZIP simulado en memoria con un ejecutable dummy
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr(local_ai.RUNNER_EXE_NAME, b"mock-llama-server-binary-content")
    zip_bytes = zip_buffer.getvalue()

    class FakeZipResponse:
        status = 200
        headers = {"Content-Length": str(len(zip_bytes))}

        def __init__(self):
            self.stream = io.BytesIO(zip_bytes)

        def read(self, chunk_size):
            return self.stream.read(chunk_size)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(local_ai.urllib.request, "urlopen", lambda req, timeout=30.0: FakeZipResponse())

    runner_dir = str(tmp_path / "bin")
    progress_calls = []

    success, msg = local_ai.download_and_extract_runner(
        runner_dir=runner_dir,
        progress_callback=lambda p, s, eta: progress_calls.append(p),
    )

    assert success is True
    assert "Runner descargado" in msg
    assert 100 in progress_calls

    extracted_exe = tmp_path / "bin" / local_ai.RUNNER_EXE_NAME
    assert extracted_exe.exists()
    assert extracted_exe.read_bytes() == b"mock-llama-server-binary-content"

    # Verificar que el zip temporal fue limpiado
    assert not (tmp_path / "bin" / ".llama_runner.zip").exists()


def test_download_and_extract_runner_blocks_zip_slip(tmp_path, monkeypatch):
    """Verifica que si el ZIP contiene rutas maliciosas hacia directorios superiores (Zip Slip), la extracción es abortada."""
    import zipfile
    import io

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("../../../malicious_payload.exe", b"malicious-payload")
    zip_bytes = zip_buffer.getvalue()

    class MaliciousZipResponse:
        status = 200
        headers = {"Content-Length": str(len(zip_bytes))}

        def __init__(self):
            self.stream = io.BytesIO(zip_bytes)

        def read(self, chunk_size):
            return self.stream.read(chunk_size)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(local_ai.urllib.request, "urlopen", lambda req, timeout=30.0: MaliciousZipResponse())

    runner_dir = str(tmp_path / "bin")
    success, msg = local_ai.download_and_extract_runner(runner_dir=runner_dir)

    assert success is False
    assert "Zip Slip" in msg
    assert not (tmp_path / "malicious_payload.exe").exists()
    assert not (tmp_path / "bin" / ".llama_runner.zip").exists()




def test_stream_openai_chat_completion_success(monkeypatch):
    lines = [
        b'data: {"choices": [{"delta": {"content": "SPEC: "}}]}\n',
        b'data: {"choices": [{"delta": {"content": "Auth Flow"}}]}\n',
        b'data: [DONE]\n',
    ]

    class MockStreamResponse:
        def __init__(self):
            self.lines = iter(lines)

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.lines)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(local_ai.urllib.request, "urlopen", lambda req, timeout=60.0: MockStreamResponse())

    tokens = list(local_ai.stream_openai_chat_completion("http://127.0.0.1:8080", "system", "user"))
    assert tokens == ["SPEC: ", "Auth Flow"]


def test_stream_openai_chat_completion_timeout_raises(monkeypatch):
    import socket
    import pytest

    class TimeoutStreamResponse:
        def __iter__(self):
            return self

        def __next__(self):
            raise socket.timeout("Read timed out")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(local_ai.urllib.request, "urlopen", lambda req, timeout=60.0: TimeoutStreamResponse())

    with pytest.raises(TimeoutError, match="stalled"):
        list(local_ai.stream_openai_chat_completion("http://127.0.0.1:8080", "system", "user", read_timeout=5.0))


def test_stream_openai_chat_completion_cancelled(monkeypatch):
    lines = [
        b'data: {"choices": [{"delta": {"content": "Token1"}}]}\n',
        b'data: {"choices": [{"delta": {"content": "Token2"}}]}\n',
    ]

    class MockStreamResponse:
        def __init__(self):
            self.lines = iter(lines)

        def __iter__(self):
            return self

        def __next__(self):
            return next(self.lines)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(local_ai.urllib.request, "urlopen", lambda req, timeout=60.0: MockStreamResponse())

    tokens = []
    for token in local_ai.stream_openai_chat_completion(
        "http://127.0.0.1:8080", "system", "user", cancel_check=lambda: len(tokens) >= 1
    ):
        tokens.append(token)

    assert tokens == ["Token1"]



