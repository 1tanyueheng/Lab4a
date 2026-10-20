"""Capture browser screenshots showing each Lab 4a question working.

Each page is loaded, driven with real clicks/input through CDP, and captured
both before and after the interaction so the report can show the behaviour.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from test_lab4a import Browser, Session  # noqa: E402

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BASE = Path(r"C:\Users\yuehe\Desktop\study\y3s1\web deve\lab4\Lab4a")
SHOTS = BASE / "screenshots"
SHOTS.mkdir(exist_ok=True)


def snap(session, name, width=900, height=720):
    session.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": False},
    )
    time.sleep(0.35)
    r = session.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": True})
    import base64

    data = base64.b64decode(r["data"])
    out = SHOTS / f"{name}.png"
    out.write_bytes(data)
    print(f"  saved {out.name} ({len(data):,} bytes)")
    return out


def main():
    br = Browser()
    try:
        s = Session(br.ws_url)
        s.call("Page.enable")
        s.call("Runtime.enable")
        fb = BASE.as_uri()

        # ---------------- Q1 ----------------
        print("Q1 ...")
        s.navigate(f"{fb}/q1/index.html")
        snap(s, "q1_before")
        s.eval("document.getElementById('changeBtn').click()")
        time.sleep(0.5)
        snap(s, "q1_after")

        # ---------------- Q2 ----------------
        print("Q2 ...")
        s.navigate(f"{fb}/q2/index.html")

        def q2_shot(value, name):
            s.eval(
                "(function(){var el=document.getElementById('userInput');"
                f"el.value={json.dumps(value)};"
                "document.getElementById('checkBtn').click();})()"
            )
            time.sleep(0.35)
            snap(s, name)

        q2_shot("5", "q2_lower")
        q2_shot("15", "q2_higher")
        q2_shot("10", "q2_equal")
        q2_shot("abc", "q2_invalid")
        q2_shot("", "q2_empty")
        q2_shot("10.5", "q2_decimal")

        # ---------------- Q3 ----------------
        print("Q3 ...")
        s.navigate(f"{fb}/q3/index.html")
        snap(s, "q3_before")
        s.eval("document.getElementById('generateBtn').click()")
        time.sleep(0.5)
        snap(s, "q3_after")
        # repeated clicks to prove no duplication
        for _ in range(3):
            s.eval("document.getElementById('generateBtn').click()")
            time.sleep(0.15)
        snap(s, "q3_repeat_clicks")

        # ---------------- Landing page ----------------
        print("index ...")
        s.navigate(f"{fb}/index.html")
        snap(s, "index")

        print("done")
    finally:
        br.close()


if __name__ == "__main__":
    main()
