PYQT_AVAILABLE = True  # PyQt imports will raise if missing; keep a flag for potential guard

from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QComboBox,
)

from src.core.logic.turn_handler import TurnHandler, init_game
from src.core.logic.deck_manager import DeckManager


# ===== PyQt Main Window ===== #
class MainWindow(QMainWindow):
    """PyQt 主窗口，使用信号/槽驱动回合推进并展示简单状态。"""

    game_updated = pyqtSignal()
    log_updated = pyqtSignal(str)

    def __init__(self, game_state):
        if not PYQT_AVAILABLE:
            raise ImportError("PyQt5 is required for MainWindow GUI. Install PyQt5 to use this UI.")
        super().__init__()
        self.game_state = game_state
        self.setWindowTitle(f"Mahjong - {game_state.rule_name}")
        self.resize(960, 720)

        # UI elements
        self._central = QWidget()
        self.setCentralWidget(self._central)
        self._layout = QVBoxLayout(self._central)

        self.rule_selector = QComboBox()
        self.rule_selector.addItems(["tencent_common", "tencent_xueliu"])
        self.status_label = QLabel("等待开始")
        self.deck_label = QLabel("")
        self.players_view = QTextEdit()
        self.players_view.setReadOnly(True)
        self.hand_container = QWidget()
        self.hand_layout = QHBoxLayout(self.hand_container)
        self.actions_container = QWidget()
        self.actions_layout = QHBoxLayout(self.actions_container)
        self.start_button = QPushButton("开始游戏")
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)

        self._layout.addWidget(self.rule_selector)
        self._layout.addWidget(self.start_button)
        self._layout.addWidget(self.status_label)
        self._layout.addWidget(self.deck_label)
        self._layout.addWidget(self.players_view)
        self._layout.addWidget(self.hand_container)
        self._layout.addWidget(self.actions_container)
        self._layout.addWidget(self.log_view)

        # Signals/slots
        self.start_button.clicked.connect(self.start_game)
        self.game_updated.connect(self._refresh_labels)
        self.log_updated.connect(self._append_log)

        # Timer drives the turn loop without blocking UI
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._tick)

        self.players_config = [
            {"name": "玩家", "is_ai": False},
            {"name": "AI-南", "is_ai": True, "ai_strategy": "advanced"},
            {"name": "AI-西", "is_ai": True, "ai_strategy": "advanced"},
            {"name": "AI-北", "is_ai": True, "ai_strategy": "advanced"},
        ]

        self.game_state = None
        self._reset_game(self.rule_selector.currentText())
        self._refresh_labels()
        self._refresh_players()
        self._render_hand_and_actions()

    @pyqtSlot()
    def start_game(self):
        """Start or resume the game loop."""
        # Always reset with the currently selected rule to honor user choice
        self._reset_game(self.rule_selector.currentText())
        if self._timer.isActive():
            self._timer.stop()
        self.log_updated.emit("游戏开始")
        self._timer.start()

    @pyqtSlot()
    def _tick(self):
        """Advance one turn slice; AI auto-plays, human waits for input."""
        gs = self.game_state
        if gs.game_stage != "playing":
            self._timer.stop()
            self.log_updated.emit("对局结束")
            return

        current = gs.current_player
        if current.is_ai:
            action = TurnHandler.process_turn(gs)
            self.log_updated.emit(f"{current.name}: {action.type} {action.card if action.card else ''}")
            self.game_updated.emit()
            return

        # Human player: ensure a drawn card exists, then wait for explicit action
        if current.drawn_card is None:
            drawn = self._draw_for_player(current)
            if drawn is None:
                self._handle_empty_deck()
                return
        self.status_label.setText(f"等待 {current.name} 选择动作…")
        self._render_hand_and_actions()
        self._timer.stop()

    @pyqtSlot(str, object)
    def handle_player_action(self, action_type: str, card=None):
        """External hook for human actions (e.g., bound to card buttons)."""
        from src.core.data.action import Action

        player = self.game_state.current_player
        action = Action(action_type, card, from_player=player)
        TurnHandler.execute_action(action, player, self.game_state)
        if action.type not in ["flower", "kong"]:
            TurnHandler.switch_player(self.game_state)
        self.log_updated.emit(f"{player.name}: {action.type} {action.card if action.card else ''}")
        self.game_updated.emit()
        self._render_hand_and_actions()
        if not self._timer.isActive():
            self._timer.start()

    def _draw_for_player(self, player):
        """Draw a card for the active player via DeckManager."""
        card = DeckManager.draw_card(self.game_state)
        player.drawn_card = card
        if card:
            player.hand.append(card)
            return card
        return None

    def _handle_empty_deck(self):
        """Handle empty wall settlement if the rule exposes a hook."""
        if hasattr(self.game_state.rule, "on_deck_empty"):
            self.game_state.rule.on_deck_empty(self.game_state)
        self.game_state.game_stage = "ended"
        self.game_updated.emit()
        self.log_updated.emit("牌墙已空，触发结算")

    @pyqtSlot()
    def _refresh_labels(self):
        deck_remaining = len(getattr(self.game_state, "deck", []))
        current = self.game_state.current_player
        self.status_label.setText(f"当前: {current.name} ({current.position}) | 分:{current.score}")
        self.deck_label.setText(f"牌墙余量: {deck_remaining}")
        self._refresh_players()

    @pyqtSlot(str)
    def _append_log(self, message: str):
        self.log_view.append(message)

    def _reset_game(self, rule_name: str):
        """Initialize a new game with the selected rule and refresh UI."""
        if self._timer.isActive():
            self._timer.stop()
        self.game_state = init_game(rule_name, self.players_config)
        self.status_label.setText(f"当前规则: {rule_name}")
        self._refresh_labels()
        self._refresh_players()
        self._render_hand_and_actions()

    def _refresh_players(self):
        """Render a text snapshot of all players (position/score/que)."""
        lines = []
        for p in self.game_state.players:
            que = getattr(p, "que_men", "-")
            lines.append(f"{p.position} {p.name} 分:{p.score} 缺:{que} 手牌:{len(p.hand)} 副露:{len(getattr(p, 'melds', []))}")
        self.players_view.setPlainText("\n".join(lines))

    def _render_hand_and_actions(self):
        """Rebuild hand buttons for the current player and action buttons for available actions."""
        # clear old widgets
        while self.hand_layout.count():
            item = self.hand_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        while self.actions_layout.count():
            item = self.actions_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        player = self.game_state.current_player
        valid = self.game_state.rule.get_valid_actions(player, self.game_state)

        # render hand buttons (primarily for discard)
        for card in sorted(player.hand, key=str):
            btn = QPushButton(str(card))
            btn.clicked.connect(lambda _=None, c=card: self.handle_player_action("discard", c))
            self.hand_layout.addWidget(btn)

        # action buttons for non-discard actions
        def add_action_btn(text, action_type):
            btn = QPushButton(text)
            btn.clicked.connect(lambda _=None: self.handle_player_action(action_type))
            self.actions_layout.addWidget(btn)

        if "hu" in valid:
            add_action_btn("胡", "hu")
        if "pong" in valid:
            add_action_btn("碰", "pong")
        if "kong" in valid:
            add_action_btn("杠", "kong")
        if "flower" in valid:
            add_action_btn("补花", "flower")
        if "must_discard_que" in valid:
            add_action_btn("必须出缺门", "discard")


def run_pyqt_ui_game(rule_name: str = "tencent_common"):
    """启动基于 PyQt 的对局窗口。"""
    if not PYQT_AVAILABLE:
        raise ImportError("PyQt5 is required for the PyQt UI. Please install PyQt5.")

    from src.core.logic.turn_handler import init_game

    players = [
        {"name": "玩家", "is_ai": False},
        {"name": "AI-南", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-西", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-北", "is_ai": True, "ai_strategy": "advanced"},
    ]
    game_state = init_game(rule_name, players)

    app = QApplication([])
    window = MainWindow(game_state)
    window.show()
    app.exec_()


if __name__ == "__main__":
    run_pyqt_ui_game()
