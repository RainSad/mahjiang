class Card:
    def __init__(self, suit: str, rank: str):
        """牌类定义
        
        Args:
            suit: 花色（万、筒、条、风、箭）
            rank: 点数（1-9或东南西北中发白）
        """
        self.suit = suit
        self.rank = rank
        self.id = f"{suit}{rank}"  # 唯一标识
        self.is_visible = False    # 是否可见（用于暗杠）
        
    def __repr__(self):
        return self.id
        
    def __eq__(self, other):
        return self.id == other.id if other else False
        
    def __hash__(self):
        return hash(self.id)