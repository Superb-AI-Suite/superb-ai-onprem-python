"""invoke over a real loopback socket: what goes on the wire and what comes back."""
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from spb_onprem import DeploymentInvokeFile, DeploymentInvokeRequest, ModelDeploymentService
from spb_onprem.model_deployments.invoke import parse_multipart
from spb_onprem.users.entities import AuthUser

DATASET_ID = "01J" + "0" * 20 + "DAT"
DEPLOYMENT_ID = "01J" + "0" * 20 + "DPX"
REPLY_BOUNDARY = "reply-boundary-1"
REPLY = (
    f"--{REPLY_BOUNDARY}\r\n"
    'Content-Disposition: form-data; name="text"\r\n'
    "Content-Type: text/plain; charset=utf-8\r\n\r\n"
    "a robot arm\r\n"
    f"--{REPLY_BOUNDARY}\r\n"
    'Content-Disposition: form-data; name="video"; filename="out.mp4"\r\n'
    "Content-Type: video/mp4\r\n\r\n"
).encode() + b"\x00\x01VIDEO" + f"\r\n--{REPLY_BOUNDARY}--\r\n".encode()


class _Relay(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.seen = {"path": self.path, "headers": dict(self.headers), "body": body}
        self.send_response(200)
        self.send_header("Content-Type", f"multipart/form-data; boundary={REPLY_BOUNDARY}")
        self.send_header("Content-Length", str(len(REPLY)))
        self.end_headers()
        self.wfile.write(REPLY)

    def log_message(self, *args):
        pass


def test_invoke_round_trip_over_a_socket(tmp_path):
    image = tmp_path / "frame.png"
    image.write_bytes(b"\x89PNG-bytes")
    server = HTTPServer(("127.0.0.1", 0), _Relay)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        service = ModelDeploymentService()
        service._auth_user = AuthUser(
            host=f"http://127.0.0.1:{server.server_address[1]}",
            access_key="test-key", access_key_secret="test-secret", is_system_sdk=False,
        )
        result = service.invoke_model_deployment(
            DATASET_ID, DEPLOYMENT_ID,
            DeploymentInvokeRequest(
                text="What is the arm holding?",
                json={"seed": 7, "note": "한글"},
                image=DeploymentInvokeFile.from_path(image),
                file=DeploymentInvokeFile.from_bytes(b"raw", "notes.bin"),
            ),
        )
    finally:
        server.shutdown()
        server.server_close()

    seen = server.seen
    assert seen["path"] == f"/graphql/model-deployments/{DATASET_ID}/{DEPLOYMENT_ID}/invoke"
    assert seen["headers"]["Authorization"].startswith("Basic ")
    content_type = seen["headers"]["Content-Type"]
    sent = parse_multipart(content_type, seen["body"])
    assert [(p.name, p.filename, p.content_type) for p in sent] == [
        ("text", None, "text/plain; charset=utf-8"),
        ("json", None, "application/json"),
        ("image", "frame.png", "image/png"),
        ("file", "notes.bin", "application/octet-stream"),
    ]
    assert sent[0].data.decode() == "What is the arm holding?"
    assert sent[1].data.decode() == '{"seed": 7, "note": "한글"}'
    assert sent[2].data == b"\x89PNG-bytes" and sent[3].data == b"raw"

    assert [(p.name, p.filename) for p in result] == [("text", None), ("video", "out.mp4")]
    assert result.parts[0].text == "a robot arm"
    assert result.videos[0].data == b"\x00\x01VIDEO"
