import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.ui.desktop.main_window import MainWindow


def run_desktop_app() -> int:
    """Run the desktop application."""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("AI Git Desktop")
    app.setOrganizationName("AI Git Desktop")

    # Set default font
    font = QFont("SF Pro", 13)
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(run_desktop_app())
