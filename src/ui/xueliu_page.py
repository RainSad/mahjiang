from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from src.ui.rule_page import RulePage


class XueliuPage(RulePage):
    """血流成河规则专用UI页面
    
    特性：
    - 显示定缺、换三张、多胡等血流特有信息
    - 提供血流规则下的动作按钮（碰、杠、胡，无吃）
    - 展示手牌并允许选择打出
    """

    def __init__(self):
        super().__init__()
        self._widget = None
        self._info_label = None
        self._exchange_label = None
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
        self._info_label = QLabel("血流成河：定缺、换三张、多胡模式")
        self._exchange_label = QLabel("")  # 换三张提示
        self._detail_label = QLabel("尚未开始")
        layout.addWidget(self._info_label)
        layout.addWidget(self._exchange_label)
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
        # 提示：换三张已在发牌后自动执行
        self._exchange_label.setText("提示：换三张已在开局后自动执行")
        self._exchange_label.setStyleSheet("color: #666;")
        
        # 汇总定缺、换三张、弃牌数等信息
        lines = []
        for p in game_state.players:
            que = getattr(p, "que_men", "-")
            changed = getattr(p, "changed_flower_count", 0)
            discarded_count = len(getattr(p, "discarded_cards", []))
            lines.append(f"{p.position} {p.name} 缺:{que} 弃牌:{discarded_count} 分:{p.score}")
        detail = "\n".join(lines) if lines else "等待开始"
        self._detail_label.setText(detail)

    def render_actions(self, player, game_state, valid_actions: list, action_callback):
        """构建血流规则的动作按钮（无吃牌）"""
        # 清空旧按钮
        while self._actions_layout.count():
            item = self._actions_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        
        # 未定缺：展示定缺选择（缺万/缺筒/缺条）
        que = getattr(player, "que_men", None)
        if not que:
            self._actions_layout.addWidget(QLabel("请选择定缺："))
            btn_wan = QPushButton("缺万")
            btn_tong = QPushButton("缺筒")
            btn_tiao = QPushButton("缺条")
            btn_wan.clicked.connect(lambda: action_callback("set_que", "万"))
            btn_tong.clicked.connect(lambda: action_callback("set_que", "筒"))
            btn_tiao.clicked.connect(lambda: action_callback("set_que", "条"))
            self._actions_layout.addWidget(btn_wan)
            self._actions_layout.addWidget(btn_tong)
            self._actions_layout.addWidget(btn_tiao)
            # 未定缺时不允许其他动作
            hint_unset = QLabel("未定缺，暂不可碰/杠/胡")
            hint_unset.setStyleSheet("color: #d35400;")
            self._actions_layout.addWidget(hint_unset)
            return
        
        # 定缺提示：若必须先打缺门牌，暂停其他动作
        if "must_discard_que" in valid_actions:
            que = getattr(player, "que_men", "")
            hint_label = QLabel(f"必须先打出缺门({que})牌！")
            hint_label.setStyleSheet("color: red; font-weight: bold;")
            self._actions_layout.addWidget(hint_label)
            return
        
        # 血流规则动作：碰、杠、胡（无吃）
        if "hu" in valid_actions:
            btn = QPushButton("胡")
            btn.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
            btn.clicked.connect(lambda: action_callback("hu", None))
            self._actions_layout.addWidget(btn)
        
        if "pong" in valid_actions:
            btn = QPushButton("碰")
            btn.clicked.connect(lambda: action_callback("pong", None))
            self._actions_layout.addWidget(btn)
        
        if "kong" in valid_actions:
            btn = QPushButton("杠")
            btn.clicked.connect(lambda: action_callback("kong", None))
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
        
        # 按花色和点数排序
        sorted_hand = sorted(player.hand, key=lambda c: (c.suit, int(c.rank) if c.rank.isdigit() else 0))
        
        # 为每张牌创建按钮
        que = getattr(player, "que_men", "")
        for card in sorted_hand:
            btn = QPushButton(str(card))
            # 缺门牌标红
            if card.suit == que:
                btn.setStyleSheet("background-color: #e74c3c; color: white;")
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
