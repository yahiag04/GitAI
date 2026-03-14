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
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QSpacerItem,
)
from PySide6.QtCore import Qt, Signal, QThread, QPropertyAnimation, QEasingCurve, Property, QSize
from PySide6.QtGui import QFont, QKeyEvent, QColor, QIcon

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


class AnimatedFrame(QFrame):
    """Frame with fade-in animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity = 0.0

    def fadeIn(self):
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(200)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()


class ChatBubble(QFrame):
    """Modern chat message bubble."""

    def __init__(self, text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setObjectName("userBubble" if is_user else "assistantBubble")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        # Sender label
        sender = QLabel("You" if is_user else "Git Assistant")
        sender.setObjectName("senderLabel")
        layout.addWidget(sender)

        # Message content
        message = QLabel(text)
        message.setWordWrap(True)
        message.setTextInteractionFlags(Qt.TextSelectableByMouse)
        message.setObjectName("messageText")
        layout.addWidget(message)

        self.setMaximumWidth(600)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)

        # Add subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)


class ChatArea(QScrollArea):
    """Scrollable chat area with modern styling."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setObjectName("chatArea")
        self.setFrameShape(QFrame.NoFrame)

        self.container = QWidget()
        self.container.setObjectName("chatContainer")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(16)
        self.layout.setContentsMargins(24, 24, 24, 24)
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

        # Scroll to bottom with slight delay for smooth effect
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def clear_messages(self) -> None:
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class InfoCard(QFrame):
    """Modern info card for sidebar."""

    def __init__(self, icon: str, title: str, value: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("infoCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setObjectName("cardIcon")
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        # Text container
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        text_layout.addWidget(title_label)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("cardValue")
        self.value_label.setWordWrap(True)
        text_layout.addWidget(self.value_label)

        layout.addLayout(text_layout, 1)

    def set_value(self, value: str):
        self.value_label.setText(value)


class StatusPanel(QFrame):
    """Modern sidebar with repository status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusPanel")
        self.setFixedWidth(280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(16)

        # Logo/Title
        header = QLabel("Git Assistant")
        header.setObjectName("sidebarTitle")
        layout.addWidget(header)

        subtitle = QLabel("Natural language Git")
        subtitle.setObjectName("sidebarSubtitle")
        layout.addWidget(subtitle)

        layout.addSpacing(8)

        # Divider
        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)

        layout.addSpacing(8)

        # Info cards
        self.branch_card = InfoCard("", "Branch", "main")
        layout.addWidget(self.branch_card)

        self.status_card = InfoCard("", "Status", "Clean")
        layout.addWidget(self.status_card)

        self.path_card = InfoCard("", "Repository", "No repo selected")
        layout.addWidget(self.path_card)

        layout.addStretch()

        # Quick actions
        actions_label = QLabel("Quick Actions")
        actions_label.setObjectName("actionsLabel")
        layout.addWidget(actions_label)

        # Action buttons
        self.smart_commit_btn = QPushButton("  Smart Commit (AI)")
        self.smart_commit_btn.setObjectName("aiButton")
        layout.addWidget(self.smart_commit_btn)

        self.commit_btn = QPushButton("  Commit Changes")
        self.commit_btn.setObjectName("actionButton")
        layout.addWidget(self.commit_btn)

        self.push_btn = QPushButton("  Push to Remote")
        self.push_btn.setObjectName("actionButton")
        layout.addWidget(self.push_btn)

        self.pull_btn = QPushButton("  Pull Latest")
        self.pull_btn.setObjectName("actionButton")
        layout.addWidget(self.pull_btn)

        layout.addSpacing(8)

        # Open folder button
        self.open_btn = QPushButton("  Open Repository")
        self.open_btn.setObjectName("primaryButton")
        layout.addWidget(self.open_btn)

    def update_status(self, branch: str, status: str, path: str) -> None:
        self.branch_card.set_value(branch)
        self.status_card.set_value(status)
        # Truncate path if too long
        if len(path) > 30:
            path = "..." + path[-27:]
        self.path_card.set_value(path)


class CommandInput(QLineEdit):
    """Modern command input field."""

    submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Type a command... (e.g., 'commit my changes')")
        self.setObjectName("commandInput")

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return and self.text().strip():
            self.submitted.emit(self.text().strip())
            self.clear()
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    """Modern main application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git Assistant")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 800)

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

        # Main chat area (center/right)
        chat_container = QWidget()
        chat_container.setObjectName("chatSection")
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Chat header
        header_widget = QWidget()
        header_widget.setObjectName("chatHeader")
        header_widget.setFixedHeight(70)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(32, 0, 32, 0)

        header_title = QLabel("Chat")
        header_title.setObjectName("chatHeaderTitle")
        header_layout.addWidget(header_title)

        header_layout.addStretch()

        clear_btn = QPushButton("Clear Chat")
        clear_btn.setObjectName("clearButton")
        clear_btn.clicked.connect(self._clear_chat)
        header_layout.addWidget(clear_btn)

        chat_layout.addWidget(header_widget)

        # Chat area
        self.chat_area = ChatArea()
        chat_layout.addWidget(self.chat_area, 1)

        # Input area
        input_widget = QWidget()
        input_widget.setObjectName("inputArea")
        input_widget.setFixedHeight(80)
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(24, 16, 24, 16)
        input_layout.setSpacing(12)

        self.command_input = CommandInput()
        input_layout.addWidget(self.command_input, 1)

        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.setFixedSize(100, 48)
        input_layout.addWidget(self.send_btn)

        chat_layout.addWidget(input_widget)

        main_layout.addWidget(chat_container, 1)

        # Welcome message
        self.chat_area.add_message(
            "Welcome! I can help you manage Git using natural language.\n\n"
            "Try commands like:\n"
            "  commit my changes\n"
            "  push\n"
            "  create branch feature-login\n"
            "  status\n"
            "  pull\n"
            "  clone user/repo",
            is_user=False,
        )

    def _apply_styles(self) -> None:
        self.setStyleSheet("""
            * {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            }

            QMainWindow {
                background-color: #0d1117;
            }

            /* Sidebar */
            #statusPanel {
                background-color: #161b22;
                border-right: 1px solid #30363d;
            }

            #sidebarTitle {
                font-size: 22px;
                font-weight: 700;
                color: #f0f6fc;
                letter-spacing: -0.5px;
            }

            #sidebarSubtitle {
                font-size: 13px;
                color: #8b949e;
                margin-top: -8px;
            }

            #divider {
                background-color: #30363d;
            }

            /* Info Cards */
            #infoCard {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 10px;
            }

            #infoCard:hover {
                background-color: #262c36;
                border-color: #3d444d;
            }

            #cardIcon {
                font-size: 18px;
                background-color: #30363d;
                border-radius: 8px;
                color: #8b949e;
            }

            #cardTitle {
                font-size: 11px;
                font-weight: 600;
                color: #8b949e;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            #cardValue {
                font-size: 14px;
                font-weight: 500;
                color: #f0f6fc;
            }

            /* Action Buttons */
            #actionsLabel {
                font-size: 11px;
                font-weight: 600;
                color: #8b949e;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 8px;
            }

            #actionButton {
                background-color: transparent;
                border: 1px solid #30363d;
                border-radius: 8px;
                color: #c9d1d9;
                padding: 10px 16px;
                text-align: left;
                font-size: 13px;
            }

            #actionButton:hover {
                background-color: #21262d;
                border-color: #3d444d;
            }

            #actionButton:pressed {
                background-color: #30363d;
            }

            #aiButton {
                background-color: #1f6feb;
                border: none;
                border-radius: 8px;
                color: #ffffff;
                padding: 10px 16px;
                text-align: left;
                font-size: 13px;
                font-weight: 600;
            }

            #aiButton:hover {
                background-color: #388bfd;
            }

            #aiButton:pressed {
                background-color: #1f6feb;
            }

            #primaryButton {
                background-color: #238636;
                border: none;
                border-radius: 8px;
                color: #ffffff;
                padding: 12px 16px;
                font-size: 14px;
                font-weight: 600;
            }

            #primaryButton:hover {
                background-color: #2ea043;
            }

            #primaryButton:pressed {
                background-color: #238636;
            }

            /* Chat Section */
            #chatSection {
                background-color: #0d1117;
            }

            #chatHeader {
                background-color: #161b22;
                border-bottom: 1px solid #30363d;
            }

            #chatHeaderTitle {
                font-size: 16px;
                font-weight: 600;
                color: #f0f6fc;
            }

            #clearButton {
                background-color: transparent;
                border: 1px solid #30363d;
                border-radius: 6px;
                color: #8b949e;
                padding: 8px 16px;
                font-size: 13px;
            }

            #clearButton:hover {
                background-color: #21262d;
                color: #c9d1d9;
            }

            /* Chat Area */
            #chatArea {
                background-color: #0d1117;
                border: none;
            }

            #chatContainer {
                background-color: #0d1117;
            }

            /* Chat Bubbles */
            #userBubble {
                background-color: #238636;
                border-radius: 16px;
                border-bottom-right-radius: 4px;
            }

            #userBubble #senderLabel {
                font-size: 11px;
                font-weight: 600;
                color: rgba(255, 255, 255, 0.8);
            }

            #userBubble #messageText {
                font-size: 14px;
                color: #ffffff;
                line-height: 1.5;
            }

            #assistantBubble {
                background-color: #21262d;
                border: 1px solid #30363d;
                border-radius: 16px;
                border-bottom-left-radius: 4px;
            }

            #assistantBubble #senderLabel {
                font-size: 11px;
                font-weight: 600;
                color: #58a6ff;
            }

            #assistantBubble #messageText {
                font-size: 14px;
                color: #c9d1d9;
                line-height: 1.5;
            }

            /* Input Area */
            #inputArea {
                background-color: #161b22;
                border-top: 1px solid #30363d;
            }

            #commandInput {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 12px;
                padding: 14px 18px;
                font-size: 14px;
                selection-background-color: #264f78;
            }

            #commandInput:focus {
                border-color: #58a6ff;
                background-color: #0d1117;
            }

            #commandInput::placeholder {
                color: #6e7681;
            }

            #sendButton {
                background-color: #238636;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
            }

            #sendButton:hover {
                background-color: #2ea043;
            }

            #sendButton:pressed {
                background-color: #238636;
            }

            #sendButton:disabled {
                background-color: #21262d;
                color: #484f58;
            }

            /* Scrollbar */
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                margin: 4px 2px;
            }

            QScrollBar::handle:vertical {
                background-color: #30363d;
                border-radius: 4px;
                min-height: 40px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #484f58;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

    def _connect_signals(self) -> None:
        self.command_input.submitted.connect(self._handle_command)
        self.send_btn.clicked.connect(self._on_send_clicked)
        self.status_panel.open_btn.clicked.connect(self._open_repository)
        self.status_panel.smart_commit_btn.clicked.connect(lambda: self._quick_command("smart commit"))
        self.status_panel.commit_btn.clicked.connect(lambda: self._quick_command("commit"))
        self.status_panel.push_btn.clicked.connect(lambda: self._quick_command("push"))
        self.status_panel.pull_btn.clicked.connect(lambda: self._quick_command("pull"))

    def _on_send_clicked(self) -> None:
        text = self.command_input.text().strip()
        if text:
            self._handle_command(text)
            self.command_input.clear()

    def _quick_command(self, cmd: str) -> None:
        self._handle_command(cmd)

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
            lines = status.split("\n")
            branch = lines[0].replace("On branch ", "") if lines else "unknown"

            # Determine status summary
            if "Nothing to commit" in status:
                status_text = "Clean"
            else:
                changes = []
                for line in lines[1:]:
                    if line.startswith("Staged:"):
                        changes.append("staged")
                    if line.startswith("Modified:"):
                        changes.append("modified")
                    if line.startswith("Untracked:"):
                        changes.append("untracked")
                status_text = ", ".join(changes).title() if changes else "Clean"

            self.status_panel.update_status(branch, status_text, str(self.working_directory))
        except ValueError:
            self.status_panel.update_status("—", "No Git repo", str(self.working_directory))

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

    def _clear_chat(self) -> None:
        self.chat_area.clear_messages()
        self.chat_area.add_message(
            "Chat cleared. How can I help you?",
            is_user=False,
        )
