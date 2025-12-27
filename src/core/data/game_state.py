class GameState:
    def __init__(self, players=None, rule=None, rule_name: str = "tencent_common"):
        """游戏状态类定义
        
        Args:
            players: 玩家列表
            rule: 规则实例
            rule_name: 使用的规则名称
        """
        self.rule_name = rule_name
        self.deck = []              # 剩余牌墙
        self.discard_pile = []      # 已打出的牌
        self.players = players or []  # 玩家列表
        self.current_player = None  # 当前回合玩家
        self.last_discarded_card = None  # 上一张打出的牌
        self.game_stage = "init"    # 游戏阶段：init/playing/ended
        self.winner = None          # 赢家
        self.round_number = 1       # 局数
        self.wind = "东"            # 场风
        self.rule = rule            # 当前规则实例
    
    def initialize_game(self):
        """初始化游戏
        
        创建初始牌组，为每个玩家发牌
        """
        if not self.rule:
            from src.rules.tencent_common.rule import TencentCommonRule
            self.rule = TencentCommonRule()
        
        # 创建初始牌组
        self.deck = self.rule.create_initial_deck()
        
        # 洗牌
        import random
        random.shuffle(self.deck)
        
        # 为每个玩家发牌（初始13张）
        for player in self.players:
            player.hand = []
            for _ in range(13):
                if self.deck:
                    player.hand.append(self.deck.pop())
        
        # 设置当前玩家（庄家）
        self.current_player = self.players[0]
        self.game_stage = "playing"