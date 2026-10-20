"""Automated browser tests for Lab 4a Q1-Q3, driven through headless Chrome.

Uses the Chrome DevTools Protocol directly (no npm dependencies) so the tests
run against the real pages in a real browser.
"""
import json
import os
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = Path(r"C:\Users\yuehe\Desktop\study\y3s1\web deve\lab4\Lab4a")
PROFILE = BASE / ".chrome-test-profile"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Browser:
    def __init__(self):
        self.port = free_port()
        if PROFILE.exists():
            shutil.rmtree(PROFILE, ignore_errors=True)
        PROFILE.mkdir(parents=True, exist_ok=True)
        self.proc = subprocess.Popen(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-first-run",
                "--no-default-browser-check",
                f"--remote-debugging-port={self.port}",
                f"--user-data-dir={PROFILE}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        self.ws_url = self._wait_for_ws()

    def _wait_for_ws(self, timeout=25):
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}/json/list", timeout=1
                ) as r:
                    targets = json.load(r)
                for t in targets:
                    if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                        return t["webSocketDebuggerUrl"]
            except Exception:
                pass
            time.sleep(0.3)
        raise RuntimeError("Chrome did not expose a debug target")

    def close(self):
        try:
            self.proc.terminate()
            self.proc.wait(timeout=10)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass
        shutil.rmtree(PROFILE, ignore_errors=True)


class Session:
    """Minimal CDP client over a raw websocket."""

    def __init__(self, ws_url):
        import base64
        import struct

        from pathlib import Path as _P

        self.base64 = base64
        self.struct = struct

        # parse ws://host:port/path
        assert ws_url.startswith("ws://")
        rest = ws_url[5:]
        hostport, _, path = rest.partition("/")
        host, _, port = hostport.partition(":")
        self.sock = socket.create_connection((host, int(port)))
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            f"GET /{path} HTTP/1.1\r\n"
            f"Host: {hostport}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(req.encode())
        # read handshake headers
        buf = b""
        while b"\r\n\r\n" not in buf:
            buf += self.sock.recv(4096)
        self._id = 0
        self.sock.settimeout(25)

    # -- websocket framing ------------------------------------------------
    def _send_frame(self, payload: bytes):
        b = self.base64
        s = self.struct
        header = bytearray()
        header.append(0x81)  # FIN + text
        mask = os.urandom(4)
        n = len(payload)
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header += s.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += s.pack(">Q", n)
        header += mask
        masked = bytes(c ^ mask[i % 4] for i, c in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                raise RuntimeError("socket closed")
            buf += chunk
        return buf

    def _recv_frame(self):
        b1, b2 = self._recv_exact(2)
        opcode = b1 & 0x0F
        masked = b2 & 0x80
        length = b2 & 0x7F
        if length == 126:
            length = self.struct.unpack(">H", self._recv_exact(2))[0]
        elif length == 127:
            length = self.struct.unpack(">Q", self._recv_exact(8))[0]
        mask = self._recv_exact(4) if masked else None
        data = self._recv_exact(length)
        if mask:
            data = bytes(c ^ mask[i % 4] for i, c in enumerate(data))
        if opcode == 0x8:
            raise RuntimeError("websocket closed by peer")
        if opcode == 0x9:
            return self._recv_frame()
        return data

    def call(self, method, params=None, timeout=25):
        self._id += 1
        mid = self._id
        msg = {"id": mid, "method": method, "params": params or {}}
        self._send_frame(json.dumps(msg).encode())
        deadline = time.time() + timeout
        while time.time() < deadline:
            raw = self._recv_frame()
            try:
                obj = json.loads(raw)
            except Exception:
                continue
            if obj.get("id") == mid:
                if "error" in obj:
                    raise RuntimeError(f"{method}: {obj['error']}")
                return obj.get("result", {})
        raise TimeoutError(method)

    def eval(self, expr):
        r = self.call(
            "Runtime.evaluate",
            {"expression": expr, "returnByValue": True, "awaitPromise": True},
        )
        res = r.get("result", {})
        if r.get("exceptionDetails"):
            raise RuntimeError(
                f"JS error: {r['exceptionDetails'].get('text')} :: {expr[:120]}"
            )
        return res.get("value")

    def navigate(self, url):
        self.call("Page.navigate", {"url": url})
        time.sleep(0.9)


results = []


def check(name, condition, detail=""):
    results.append((bool(condition), name, detail))
    mark = "PASS" if condition else "FAIL"
    print(f"[{mark}] {name}" + (f"  -> {detail}" if detail and not condition else ""))


def main():
    br = Browser()
    try:
        s = Session(br.ws_url)
        s.call("Page.enable")
        s.call("Runtime.enable")

        file_base = BASE.as_uri()

        # ============================ Q1 ============================
        print("\n=== Q1: Interactive Text Changer ===")
        s.navigate(f"{file_base}/q1/index.html")

        check(
            "Q1 initial paragraph text",
            s.eval("document.getElementById('message').textContent") == "Welcome to my website!",
            s.eval("document.getElementById('message').textContent"),
        )
        check("Q1 changeMessage is a function", s.eval("typeof changeMessage") == "function")
        check(
            "Q1 listener attached (onclick not used)",
            s.eval("document.getElementById('changeBtn').onclick") is None,
        )

        s.eval("document.getElementById('changeBtn').click()")
        time.sleep(0.15)
        check(
            "Q1 click replaces text with 'Hello there!'",
            s.eval("document.getElementById('message').textContent") == "Hello there!",
            s.eval("document.getElementById('message').textContent"),
        )
        check(
            "Q1 status region updated",
            "Hello there!" in (s.eval("document.getElementById('status').textContent") or ""),
        )

        # second click must not break or duplicate
        s.eval("document.getElementById('changeBtn').click()")
        time.sleep(0.1)
        check(
            "Q1 repeated click stays stable",
            s.eval("document.getElementById('message').textContent") == "Hello there!",
        )
        check(
            "Q1 exactly one paragraph in container",
            s.eval("document.querySelectorAll('#myElement p').length") == 1,
        )

        # ============================ Q2 ============================
        print("\n=== Q2: Smart Number Validator ===")
        s.navigate(f"{file_base}/q2/index.html")
        check("Q2 checkInput is a function", s.eval("typeof checkInput") == "function")
        check(
            "Q2 result starts empty",
            (s.eval("document.getElementById('result').textContent") or "") == "",
        )

        def q2(value):
            s.eval(
                "(function(){var el=document.getElementById('userInput');"
                f"el.value={json.dumps(value)};"
                "document.getElementById('checkBtn').click();})()"
            )
            time.sleep(0.1)
            return s.eval("document.getElementById('result').textContent")

        cases = [
            ("5", "The number is lower than 10"),
            ("10", "The number is equal to 10"),
            ("15", "The number is higher than 10"),
            ("abc", "Please enter a valid number!"),
            ("", "Please enter a valid number!"),
            ("   ", "Please enter a valid number!"),
            ("10.5", "The number is higher than 10"),
            ("9.99", "The number is lower than 10"),
            ("-4", "The number is lower than 10"),
            ("0", "The number is lower than 10"),
            ("12px", "Please enter a valid number!"),
        ]
        for inp, expected in cases:
            got = q2(inp)
            check(f"Q2 input {inp!r} -> {expected!r}", got == expected, f"got {got!r}")

        # colour state class present
        q2("5")
        check(
            "Q2 state class applied for 'low'",
            s.eval("document.getElementById('result').classList.contains('is-low')") is True,
        )
        q2("abc")
        check(
            "Q2 state class switches to invalid (no stacking)",
            s.eval(
                "document.getElementById('result').classList.contains('is-invalid')"
                " && !document.getElementById('result').classList.contains('is-low')"
            )
            is True,
        )

        # Enter key triggers the check
        s.eval("document.getElementById('userInput').value='15'")
        s.eval(
            "document.getElementById('userInput').dispatchEvent("
            "new KeyboardEvent('keydown',{key:'Enter',bubbles:true}))"
        )
        time.sleep(0.1)
        check(
            "Q2 Enter key triggers check",
            s.eval("document.getElementById('result').textContent") == "The number is higher than 10",
        )

        # ============================ Q3 ============================
        print("\n=== Q3: Dynamic Number Generator ===")
        s.navigate(f"{file_base}/q3/index.html")
        check("Q3 generateNumbers is a function", s.eval("typeof generateNumbers") == "function")
        check(
            "Q3 list starts empty",
            s.eval("document.getElementById('numberList').children.length") == 0,
        )

        s.eval("document.getElementById('generateBtn').click()")
        time.sleep(0.15)
        items = s.eval(
            "Array.from(document.querySelectorAll('#numberList li')).map(function(li){return li.textContent;})"
        )
        expected_items = [f"The number is {i}" for i in range(1, 6)]
        check("Q3 generates 5 items", len(items) == 5, str(items))
        check("Q3 items have correct text 1..5", items == expected_items, str(items))
        check(
            "Q3 items are real <li> elements inside <ol>",
            s.eval(
                "document.getElementById('numberList').tagName === 'OL' && "
                "Array.from(document.getElementById('numberList').children).every(function(e){return e.tagName==='LI';})"
            )
            is True,
        )

        # repeated clicks must not duplicate
        for _ in range(3):
            s.eval("document.getElementById('generateBtn').click()")
            time.sleep(0.1)
        after = s.eval("document.getElementById('numberList').children.length")
        check("Q3 repeated clicks do not duplicate (still 5)", after == 5, f"got {after}")

        repeated = s.eval(
            "Array.from(document.querySelectorAll('#numberList li')).map(function(li){return li.textContent;})"
        )
        check("Q3 list identical after repeated clicks", repeated == expected_items, str(repeated))

        print("\n" + "=" * 62)
        passed = sum(1 for ok, _, _ in results if ok)
        total = len(results)
        print(f"RESULT: {passed}/{total} checks passed")
        failed = [(n, d) for ok, n, d in results if not ok]
        if failed:
            print("FAILURES:")
            for n, d in failed:
                print(f"  - {n}  {d}")
        return 0 if not failed else 1
    finally:
        br.close()


if __name__ == "__main__":
    raise SystemExit(main())
