import os
import sys
import traceback
from pathlib import Path

import config
from core import autostart
from core.singleton import SingleInstance
from core.supervisor import Supervisor, child_python

ROOT = Path(__file__).resolve().parent
LOG_DIR = config.DATA_DIR / "logs"
LOG_PATH = LOG_DIR / "prometheus.log"
COLORS = {
    "running": (46, 160, 67),
    "restarting": (219, 171, 9),
    "paused": (128, 128, 128),
    "failed": (207, 34, 46),
}
LABELS = {
    "running": "Listening",
    "restarting": "Restarting",
    "paused": "Paused",
    "failed": "Stopped after repeated errors",
}


def make_icon(color):
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((4, 4, 60, 60), fill=color + (255,))
    draw.polygon([(24, 18), (24, 46), (46, 32)], fill=(255, 255, 255, 255))
    return image


def pythonw() -> str:
    exe = Path(sys.executable)
    candidate = exe.with_name("pythonw.exe")
    return str(candidate if candidate.exists() else exe)


def build_supervisor(on_state=None) -> Supervisor:
    return Supervisor(
        [child_python(), "main.py", "console"],
        ROOT,
        LOG_PATH,
        on_state=on_state,
        env={"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
    )


def open_path(path: Path) -> None:
    if hasattr(os, "startfile"):
        os.startfile(path)


def run_tray() -> None:
    import pystray

    guard = SingleInstance()
    if not guard.acquire():
        return
    holder = {}

    def on_state(state):
        icon = holder.get("icon")
        if not icon:
            return
        icon.icon = make_icon(COLORS[state])
        icon.title = f"Prometheus: {LABELS[state]}"
        if state == "failed":
            icon.notify("Prometheus keeps stopping. Open the log from the tray menu.", "Prometheus")

    sup = build_supervisor(on_state)

    def toggle(icon, item):
        sup.stop() if sup.active else sup.start()

    def toggle_autostart(icon, item):
        autostart.disable() if autostart.is_enabled() else autostart.enable(ROOT, pythonw())

    def quit_app(icon, item):
        sup.close()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem(lambda item: f"Prometheus: {LABELS[sup.state]}", None, enabled=False),
        pystray.MenuItem(lambda item: "Pause listening" if sup.active else "Resume listening", toggle, default=True),
        pystray.MenuItem("Restart", lambda icon, item: sup.restart()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open workspace folder", lambda icon, item: open_path(config.WORKSPACE_DIR)),
        pystray.MenuItem("Open log", lambda icon, item: open_path(LOG_PATH)),
        pystray.MenuItem("Start with Windows", toggle_autostart, checked=lambda item: autostart.is_enabled()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit Prometheus", quit_app),
    )
    icon = pystray.Icon("prometheus", make_icon(COLORS["paused"]), "Prometheus", menu)
    holder["icon"] = icon
    sup.start()
    icon.run()
    guard.release()


def check() -> None:
    sup = build_supervisor()
    print("child command:", sup.command)
    print("project folder:", ROOT)
    print("log file:", LOG_PATH)
    print("start with Windows enabled:", autostart.is_enabled())
    print("icon renders:", make_icon(COLORS["running"]).size)
    sup.close()


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        try:
            run_tray()
        except Exception:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            (LOG_DIR / "tray-error.log").write_text(traceback.format_exc(), encoding="utf-8")
            raise
