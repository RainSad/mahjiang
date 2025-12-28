from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from src.ui.rule_page import RulePage


class CommonPage(RulePage):
    """腾讯大众麻将规则专用UI页面
    
    特性：
    - 显示风位、花牌信息
    - 提供大众麻将的动作按钮（吃、碰、杠、胡）
    - 展示手牌并允许选择打出
    """

    def __init__(self):
        super().__init__()
        self._widget = None
        self._info_label = None
        self._detail_label = None
        self._hand_container = None
        self._hand_layout = None
        self._actions_container = None
        self._actions_layout = None

    def setup_ui(self, parent: QWidget):
        """初始化UI组件"""
        self._widget = QWidget(parent)
        layout = QVBoxLayout(self._widget)
        
        # 规则信息标签
        self._info_label = QLabel("腾讯大众：吃碰杠胡、风箭花牌")
        self._detail_label = QLabel("尚未开始")
        layout.addWidget(self._info_label)
        layout.addWidget(self._detail_label)
        
        # 手牌区域
        self._hand_container = QWidget()
        self._hand_layout = QHBoxLayout(self._hand_container)
        layout.addWidget(QLabel("手牌:"))
        layout.addWidget(self._hand_container)
        
        # 动作区域
        self._actions_container = QWidget()
        self._actions_layout = QHBoxLayout(self._actions_container)
        layout.addWidget(QLabel("动作:"))
        layout.addWidget(self._actions_container)
        
        return self._widget

    def render_state(self, game_state):
        """根据游戏状态刷新显示"""
        if not game_state:
            self._detail_label.setText("尚未开始")
            return
        
        # 汇总场风、门风、花牌等信息
        lines = []
        for p in game_state.players:
            wind = getattr(p, "wind", p.position)
            flowers = sum(1 for m in getattr(p, "melds", []) if getattr(m, "type", "") == "补花")
            dealer_mark = "庄" if p.is_dealer else ""
            lines.append(f"{p.position}{dealer_mark} {p.name} 风:{wind} 花:{flowers} 分:{p.score}")
        
        game_wind = getattr(game_state, "wind", "东")
        detail = f"场风: {game_wind}\n" + "\n".join(lines)
        self._detail_label.setText(detail)

    def render_actions(self, player, game_state, valid_actions: list, action_callback):
        """构建大众麻将的动作按钮（含吃牌）"""
        # 清空旧按钮
        while self._actions_layout.count():
            item = self._actions_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        # 大众麻将动作：吃、碰、杠、胡
        if "hu" in valid_actions:
            btn = QPushButton("胡")
            btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            btn.clicked.connect(lambda: action_callback("hu", None))
            self._actions_layout.addWidget(btn)
        
        if "pong" in valid_actions:
            btn = QPushButton("碰")
            btn.clicked.connect(lambda: action_callback("pong", None))
            self._actions_layout.addWidget(btn)
        
        if "chow" in valid_actions:
            btn = QPushButton("吃")
            btn.clicked.connect(lambda: action_callback("chow", None))
            self._actions_layout.addWidget(btn)
        
        if "kong" in valid_actions:
            btn = QPushButton("杠")
            btn.clicked.connect(lambda: action_callback("kong", None))
            self._actions_layout.addWidget(btn)
        
        if "flower" in valid_actions:
            btn = QPushButton("补花")
            btn.setStyleSheet("background-color: #9b59b6; color: white;")
            btn.clicked.connect(lambda: action_callback("flower", None))
            self._actions_layout.addWidget(btn)
        
        # 过
        pass_btn = QPushButton("过/打牌")
        pass_btn.clicked.connect(lambda: action_callback("pass", None))
        self._actions_layout.addWidget(pass_btn)

    def render_hand(self, player, action_callback):
        """渲染玩家手牌按钮"""
        # 清空旧按钮
        while self._hand_layout.count():
            item = self._hand_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        # 按花色和点数排序（花牌放最后）
        def sort_key(c):
            suit_order = {'万': 0, '筒': 1, '条': 2, '风': 3, '箭': 4, '花': 5}
            suit_idx = suit_order.get(c.suit, 6)
            rank_val = int(c.rank) if c.rank.isdigit() else 0
            return (suit_idx, rank_val, c.rank)
        
        sorted_hand = sorted(player.hand, key=sort_key)
        
        # 为每张牌创建按钮
        for card in sorted_hand:
            btn = QPushButton(str(card))
            # 花牌标记为特殊颜色
            if card.suit == "花":
                btn.setStyleSheet("background-color: #9b59b6; color: white;")
            btn.clicked.connect(lambda checked, c=card: action_callback("discard", c))
            self._hand_layout.addWidget(btn)

    def reset(self):
        """重置页面状态"""
        if self._detail_label:
            self._detail_label.setText("尚未开始")
        # 清空手牌和动作按钮
        if self._hand_layout:
            while self._hand_layout.count():
                item = self._hand_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
        if self._actions_layout:
            while self._actions_layout.count():
                item = self._actions_layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()

    def get_widget(self) -> QWidget:
        """返回页面的顶层widget"""
        return self._widget
