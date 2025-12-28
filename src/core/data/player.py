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
        self.last_action = None     # 上一次操作
        self.consecutive_gang_count = 0  # 连续杠次数
        self.changed_flower_count = 0    # 补花次数
        self.is_ji_hu = False       # 是否是鸡胡
        self.ji_hu_from = None      # 鸡胡来源（自摸/点炮）
        self.last_gang_gain = 0     # 最近一次杠获得的分数（用于呼叫转移）
        self.is_tian_hu = False     # 天胡标志
        self.is_di_hu = False       # 地胡标志
        self.is_tian_hu_candidate = False   # 天胡候选（庄家首圈）
        self.is_di_hu_candidate = False     # 地胡候选（闲家首圈摸牌）
        self.que_men = None         # 定缺花色（万/筒/条）
        self.que_men_locked = False # 定缺是否已锁定（不可更改）
        self.discarded_cards = []   # 已打出的牌（用于检查天命花猪）
        self.total_gang_gain = 0    # 本局从杠牌获得的总分
        self.total_gang_loss = 0    # 本局因杠牌损失的总分
        self.gang_events = []       # 本局每次杠的收益事件明细：[{type, gain, contributors:{player:amount}}]
        self.last_gang_event = None # 最近一次杠事件（用于呼叫转移）