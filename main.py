from __future__ import annotations
import sys
import os
from pathlib import Path

# Ensure the project root is on sys.path when launched as a script
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from settings import Settings
import startup


def ensure_sprites():
    sprite_dir = PROJECT_ROOT / "assets" / "sprites"
    sprite_dir.mkdir(parents=True, exist_ok=True)
    if not any(sprite_dir.glob("*.png")):
        print("Generating pixel sprites…")
        sys.path.insert(0, str(PROJECT_ROOT / "assets"))
        try:
            import generate_sprites
            generate_sprites.generate_all()
        except Exception as e:
            print(f"Warning: sprite generation failed – {e}")
            print("App will run with placeholder (transparent) sprites.")


def main():
    # High-DPI support
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("PixelLion")
    app.setOrganizationName("PixelLion")
    app.setQuitOnLastWindowClosed(False)   # keep alive via tray

    # Pixel-perfect rendering: disable font antialiasing effects
    font = QFont()
    font.setStyleStrategy(QFont.StyleStrategy.NoAntialias)
    app.setFont(font)

    ensure_sprites()

    settings = Settings()
    startup.sync_startup(settings.start_with_windows)

    # Import here so Qt app exists before widget construction
    from lion import LionWindow
    window = LionWindow(settings)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
