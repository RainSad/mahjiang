from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget


class XueliuPage(QWidget):
    """血流成河规则专用的简单信息面板。

    目前展示定缺/换三张/多胡提示，可在后续扩展成完整交互面板。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.info_label = QLabel("血流成河：定缺、换三张、多胡模式")
        self.detail_label = QLabel("尚未开始")
        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.detail_label)

    def update_state(self, game_state):
        """根据游戏状态刷新显示。"""
        if not game_state:
            self.detail_label.setText("尚未开始")
            return
        # 汇总定缺、换三张、弃牌数等信息
        lines = []
        for p in game_state.players:
            que = getattr(p, "que_men", "-")
            changed = getattr(p, "changed_flower_count", 0)
            lines.append(f"{p.position} {p.name} 缺:{que} 补花:{changed} 分:{p.score}")
        detail = "\n".join(lines) if lines else "等待开始"
        self.detail_label.setText(detail)
