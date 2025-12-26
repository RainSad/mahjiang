from datetime import datetime


class Meld:
    """副露/面子信息，供计分与行牌流程使用"""

    def __init__(self, meld_type: str, cards: list, from_player=None, concealed: bool = False):
        self.type = meld_type          # 吃/碰/明杠/暗杠/补杠/补花/花
        self.cards = list(cards)
        self.from_player = from_player
        self.concealed = concealed

    def __repr__(self):
        cards_str = ','.join(str(c) for c in self.cards)
        return f"Meld(type={self.type}, cards=[{cards_str}])"

class Action:
    def __init__(self, action_type: str, card: 'Card' = None, from_player=None):
        """操作类定义
        
        Args:
            action_type: 操作类型（draw/discard/chow/pong/kong/hu）
            card: 涉及的牌
            from_player: 来源玩家
        """
        self.type = action_type
        self.card = card
        self.from_player = from_player
        self.timestamp = datetime.now()  # 操作时间戳
        
    def __repr__(self):
        return f"Action(type={self.type}, card={self.card}, from={self.from_player.name if self.from_player else 'None'})"