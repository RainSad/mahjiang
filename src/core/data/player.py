class Player:
    def __init__(self, name: str, is_ai: bool = True):
        """玩家类定义
        
        Args:
            name: 玩家名称
            is_ai: 是否为AI玩家
        """
        self.name = name
        self.is_ai = is_ai
        self.hand = []              # 手牌
        self.melds = []             # 吃碰杠的牌
        self.score = 0              # 分数
        self.position = None        # 位置：东、南、西、北
        self.is_dealer = False      # 是否是庄家
        self.drawn_card = None      # 当前摸到的牌
        self.ai_strategy = None     # AI策略
        self.previous_player = None # 上家
        self.next_player = None     # 下家