#!/usr/bin/env python3
from collections import defaultdict, deque
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import secrets
import sys
import time
import uuid

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

os.makedirs("logs", exist_ok=True)
logger = logging.getLogger("SecurityAudit")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(
    "logs/security_audit.jsonl",
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)
logger.addHandler(file_handler)


def log_event(level: str, component: str, req_id: str, subject: str,
              action: str, result: str, source_ip: str, details: str = ""):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "component": component,
        "request_id": req_id,
        "subject": subject,
        "action": action,
        "result": result,
        "source_ip": source_ip,
        "details": details
    }
    line = json.dumps(record, ensure_ascii=False)
    getattr(logger, level.lower(), logger.info)(line)
    print(line)


class SecurityMonitor:
    def __init__(self, brute_force_limit: int = 5, window_sec: int = 60):
        self.total_requests = 0
        self.error_count = 0
        self.failed_auths = defaultdict(deque)
        self.limit = brute_force_limit
        self.window = window_sec

    def record_request(self, status_code: int):
        self.total_requests += 1
        if status_code >= 400:
            self.error_count += 1

    def record_failed_auth(self, ip: str, req_id: str, client_id: str):
        now = time.time()
        attempts = self.failed_auths[ip]
        attempts.append(now)
        while attempts and now - attempts[0] > self.window:
            attempts.popleft()

        if len(attempts) >= self.limit:
            log_event(
                "CRITICAL", "monitor", req_id, client_id or "anonymous",
                "BRUTE_FORCE_ALERT", "alert", ip,
                f"Виявлено {len(attempts)} невдалих спроб входу за {self.window} с"
            )

    def get_metrics(self) -> dict:
        return {
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "monitored_ips": len(self.failed_auths)
        }


CLIENTS = {"rose-01": "A7mQ2pL9xR4v", "tulip-02": "K3zN8tW5cY1s"}
TOKENS = {}
MONITOR = SecurityMonitor()


def mask_token(token: str) -> str:
    return "sha256:" + hashlib.sha256(token.encode()).hexdigest()[:8]


class MonitoredHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _send_json(self, code: int, payload: dict, req_id: str):
        MONITOR.record_request(code)
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Request-ID", req_id)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        req_id = self.headers.get("X-Request-ID") or str(uuid.uuid4())
        ip = self.client_address[0]

        if self.path != "/auth/token":
            log_event("WARNING", "api", req_id, "anonymous", f"POST {self.path}", "not_found", ip)
            return self._send_json(404, {"error": "not_found"}, req_id)

        length = int(self.headers.get("Content-Length", 0))
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except Exception:
            log_event("WARNING", "auth", req_id, "anonymous", "POST /auth/token", "bad_request", ip)
            return self._send_json(400, {"error": "invalid_json"}, req_id)

        cid = str(data.get("client_id", ""))
        secret = str(data.get("client_secret", ""))

        if CLIENTS.get(cid) != secret:
            log_event("WARNING", "auth", req_id, cid or "anonymous",
                      "POST /auth/token", "denied", ip, "Невірний client_id або secret")
            MONITOR.record_failed_auth(ip, req_id, cid)
            return self._send_json(401, {"error": "invalid_credentials"}, req_id)

        token = secrets.token_urlsafe(24)
        TOKENS[token] = cid
        log_event("INFO", "auth", req_id, cid, "POST /auth/token", "success", ip,
                  f"Видано токен ({mask_token(token)})")
        self._send_json(200, {"access_token": token, "token_type": "Bearer"}, req_id)

    def do_GET(self):
        req_id = self.headers.get("X-Request-ID") or str(uuid.uuid4())
        ip = self.client_address[0]

        if self.path == "/metrics":
            log_event("INFO", "monitor", req_id, "system", "GET /metrics", "success", ip)
            return self._send_json(200, MONITOR.get_metrics(), req_id)

        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            log_event("WARNING", "api", req_id, "anonymous", f"GET {self.path}", "unauthorized", ip,
                      "Відсутній Bearer-токен")
            return self._send_json(401, {"error": "missing_token"}, req_id)

        token = auth[7:].strip()
        subject = TOKENS.get(token)
        if not subject:
            log_event("WARNING", "api", req_id, "unknown", f"GET {self.path}", "unauthorized", ip,
                      f"Недійсний токен ({mask_token(token)})")
            return self._send_json(401, {"error": "invalid_token"}, req_id)

        if self.path == "/whoami":
            log_event("INFO", "api", req_id, subject, "GET /whoami", "success", ip)
            return self._send_json(200, {"client_id": subject, "role": "reader"}, req_id)

        log_event("WARNING", "api", req_id, subject, f"GET {self.path}", "not_found", ip)
        self._send_json(404, {"error": "not_found"}, req_id)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8081), MonitoredHandler)
    log_event("INFO", "system", "startup", "system", "SERVER_START", "success", "127.0.0.1",
              "Сервер моніторингу запущено на http://127.0.0.1:8081")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log_event("INFO", "system", "shutdown", "system", "SERVER_STOP", "success", "127.0.0.1")
        server.server_close()
