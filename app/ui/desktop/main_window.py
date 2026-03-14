from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QLabel,
    QFrame,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont, QKeyEvent

from app.controllers.assistant_controller import handle_user_prompt, handle_confirmed_action
from core.action_router.route_action import RouteDependencies
from core.command_parser.parse_command import parse_command
from core.git_engine.service import create_git_engine, GitEngine
from core.github_service.service import create_github_service, GitHubService


class CommandWorker(QThread):
    """Worker thread to execute commands without blocking UI."""

    finished = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        prompt: str,
        dependencies: RouteDependencies,
        confirmed: bool = False,
        parsed_result=None,
    ):
        super().__init__()
        self.prompt = prompt
        self.dependencies = dependencies
        self.confirmed = confirmed
        self.parsed_result = parsed_result

    def run(self) -> None:
        try:
            if self.confirmed and self.parsed_result:
                result = handle_confirmed_action(self.parsed_result, self.dependencies)
            else:
                result = handle_user_prompt(self.prompt, self.dependencies)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ChatBubble(QFrame):
    """A chat message bubble."""

    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.setObjectName("userBubble" if is_user else "assistantBubble")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(label)

        self.setMaximumWidth(500)


class ChatArea(QScrollArea):
    """Scrollable chat area containing message bubbles."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setObjectName("chatArea")

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(10)
        self.layout.addStretch()

        self.setWidget(self.container)

    def add_message(self, text: str, is_user: bool) -> None:
        bubble = ChatBubble(text, is_user)

        # Insert before the stretch
        self.layout.insertWidget(self.layout.count() - 1, bubble)

        # Align user messages right, assistant left
        if is_user:
            self.layout.setAlignment(bubble, Qt.AlignRight)
        else:
            self.layout.setAlignment(bubble, Qt.AlignLeft)

        # Scroll to bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_messages(self) -> None:
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class StatusPanel(QFrame):
    """Side panel showing repository status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusPanel")
        self.setFixedWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Repository Status")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        # Status content
        self.status_label = QLabel("No repository selected")
        self.status_label.setWordWrap(True)
        self.status_label.setObjectName("statusContent")
        layout.addWidget(self.status_label)

        # Path label
        self.path_label = QLabel("")
        self.path_label.setWordWrap(True)
        self.path_label.setObjectName("pathLabel")
        layout.addWidget(self.path_label)

        layout.addStretch()

        # Open folder button
        self.open_btn = QPushButton("Open Repository")
        self.open_btn.setObjectName("openButton")
        layout.addWidget(self.open_btn)

    def update_status(self, status: str, path: str = "") -> None:
        self.status_label.setText(status)
        if path:
            self.path_label.setText(f"Path: {path}")


class CommandInput(QLineEdit):
    """Command input field with Enter key handling."""

    submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Type a Git command in plain English...")
        self.setObjectName("commandInput")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return and self.text().strip():
            self.submitted.emit(self.text().strip())
            self.clear()
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Git Desktop")
        self.setMinimumSize(900, 600)

        # Initialize services
        self.working_directory = Path.cwd()
        self.git_engine: GitEngine = create_git_engine(self.working_directory)
        self.github_service: GitHubService = create_github_service()
        self.dependencies = RouteDependencies(
            git_engine=self.git_engine,
            github_service=self.github_service,
        )

        # Pending confirmation state
        self.pending_confirmation = None

        self._setup_ui()
        self._apply_styles()
        self._connect_signals()
        self._update_status()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Status panel (left side)
        self.status_panel = StatusPanel()
        main_layout.addWidget(self.status_panel)

        # Chat area (center/right)
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(15)

        # Header
        header = QLabel("AI Git Desktop")
        header.setObjectName("header")
        chat_layout.addWidget(header)

        # Chat area
        self.chat_area = ChatArea()
        chat_layout.addWidget(self.chat_area)

        # Input area
        input_layout = QHBoxLayout()
        self.command_input = CommandInput()
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(self.send_btn)
        chat_layout.addLayout(input_layout)

        main_layout.addWidget(chat_container, 1)

        # Welcome message
        self.chat_area.add_message(
            "Welcome to AI Git Desktop!\n\n"
            "You can manage Git using natural language.\n\n"
            "Examples:\n"
            "- commit my changes\n"
            "- create a branch called feature-login\n"
            "- push my project\n"
            "- open a pull request from dev to main",
            is_user=False,
        )

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }

            #header {
                font-size: 24px;
                font-weight: bold;
                color: #cdd6f4;
                padding: 10px 0;
            }

            #chatArea {
                background-color: #1e1e2e;
                border: none;
            }

            #userBubble {
                background-color: #89b4fa;
                color: #1e1e2e;
                border-radius: 12px;
            }

            #assistantBubble {
                background-color: #313244;
                color: #cdd6f4;
                border-radius: 12px;
            }

            #commandInput {
                background-color: #313244;
                color: #cdd6f4;
                border: 2px solid #45475a;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }

            #commandInput:focus {
                border-color: #89b4fa;
            }

            #sendButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }

            #sendButton:hover {
                background-color: #b4befe;
            }

            #sendButton:pressed {
                background-color: #74c7ec;
            }

            #statusPanel {
                background-color: #181825;
                border-right: 1px solid #313244;
            }

            #panelTitle {
                font-size: 16px;
                font-weight: bold;
                color: #cdd6f4;
                padding-bottom: 10px;
            }

            #statusContent {
                color: #a6adc8;
                font-size: 13px;
                line-height: 1.5;
            }

            #pathLabel {
                color: #6c7086;
                font-size: 11px;
                padding-top: 10px;
            }

            #openButton {
                background-color: #45475a;
                color: #cdd6f4;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }

            #openButton:hover {
                background-color: #585b70;
            }

            QScrollBar:vertical {
                background-color: #1e1e2e;
                width: 8px;
            }

            QScrollBar::handle:vertical {
                background-color: #45475a;
                border-radius: 4px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
        """)

    def _connect_signals(self) -> None:
        self.command_input.submitted.connect(self._handle_command)
        self.send_btn.clicked.connect(self._on_send_clicked)
        self.status_panel.open_btn.clicked.connect(self._open_repository)

    def _on_send_clicked(self) -> None:
        text = self.command_input.text().strip()
        if text:
            self._handle_command(text)
            self.command_input.clear()

    def _handle_command(self, prompt: str) -> None:
        # Add user message
        self.chat_area.add_message(prompt, is_user=True)

        # Handle confirmation responses
        if self.pending_confirmation:
            if prompt.lower() in ("yes", "y"):
                self._execute_confirmed_action()
            else:
                self.chat_area.add_message("Action cancelled.", is_user=False)
                self.pending_confirmation = None
            return

        # Parse the command
        parsed = parse_command(prompt)

        # Check if confirmation is needed
        if parsed.requires_confirmation:
            self.pending_confirmation = parsed
            self.chat_area.add_message(parsed.confirmation_message, is_user=False)
            return

        # Execute command in background thread
        self._execute_command(prompt)

    def _execute_command(self, prompt: str) -> None:
        self.command_input.setEnabled(False)
        self.send_btn.setEnabled(False)

        self.worker = CommandWorker(prompt, self.dependencies)
        self.worker.finished.connect(self._on_command_finished)
        self.worker.error.connect(self._on_command_error)
        self.worker.start()

    def _execute_confirmed_action(self) -> None:
        self.command_input.setEnabled(False)
        self.send_btn.setEnabled(False)

        self.worker = CommandWorker(
            "",
            self.dependencies,
            confirmed=True,
            parsed_result=self.pending_confirmation,
        )
        self.worker.finished.connect(self._on_command_finished)
        self.worker.error.connect(self._on_command_error)
        self.worker.start()
        self.pending_confirmation = None

    def _on_command_finished(self, result: str) -> None:
        self.chat_area.add_message(result, is_user=False)
        self.command_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.command_input.setFocus()
        self._update_status()

    def _on_command_error(self, error: str) -> None:
        self.chat_area.add_message(f"Error: {error}", is_user=False)
        self.command_input.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.command_input.setFocus()

    def _update_status(self) -> None:
        try:
            status = self.git_engine.get_status()
            self.status_panel.update_status(status, str(self.working_directory))
        except ValueError:
            self.status_panel.update_status(
                "Not a Git repository",
                str(self.working_directory),
            )

    def _open_repository(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Repository",
            str(Path.home()),
        )
        if directory:
            self.working_directory = Path(directory)
            self.git_engine = create_git_engine(self.working_directory)
            self.dependencies = RouteDependencies(
                git_engine=self.git_engine,
                github_service=self.github_service,
            )
            self._update_status()
            self.chat_area.add_message(
                f"Opened repository: {directory}",
                is_user=False,
            )
