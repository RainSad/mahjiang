# 方法1：使用 Optional 类型
from typing import Optional
from src.rules.base_rule import BaseRule

class GameState:
    def __init__(self, rule_name: str = "tencent_common"):
        """游戏状态类定义
        
        Args:
            rule_name: 使用的规则名称
        """
        self.rule_name = rule_name
        self.deck = []              # 剩余牌墙
        self.discard_pile = []      # 已打出的牌
        self.players = []           # 玩家列表
        self.current_player = None  # 当前回合玩家
        self.last_discarded_card = None  # 上一张打出的牌
        self.game_stage = "init"    # 游戏阶段：init/playing/ended
        self.winner = None          # 赢家
        self.winners = []           # 多家胡时的赢家列表（按顺序）
        self.round_number = 1       # 局数
        self.wind = "东"            # 场风
        self.rule: Optional[BaseRule] = None  # 当前规则实例
        self.settlement_logs = []   # 结算明细日志（查花猪/查大叫/退税等）