import random

from src.core.data.card import Card

class DeckManager:
    """牌墙管理类"""
    
    @staticmethod
    def create_initial_deck(rule) -> list:
        """创建初始牌组
        
        Args:
            rule: 规则实例
        
        Returns:
            初始牌组
        """
        return rule.create_initial_deck()
    
    @staticmethod
    def shuffle(deck) -> list:
        """洗牌
        
        Args:
            deck: 牌组
        
        Returns:
            洗牌后的牌组
        """
        shuffled = deck.copy()
        random.shuffle(shuffled)
        return shuffled
    
    @staticmethod
    def deal(game_state) -> None:
        """发牌
        
        Args:
            game_state: 游戏状态实例
        """
        rule = game_state.rule
        players = game_state.players
        deck = game_state.deck
        
        # 每个玩家初始手牌数
        starting_tiles = rule.starting_tiles
        
        # 发牌：顺时针方向，每次发一张牌
        for _ in range(starting_tiles):
            for player in players:
                card = deck.pop()
                player.hand.append(card)
        
        # 庄家额外多一张牌
        if rule.dealer_extra_tile:
            dealer = next(p for p in players if p.is_dealer)
            dealer.hand.append(deck.pop())
    
    @staticmethod
    def draw_card(game_state) -> Card:
        """从牌墙摸牌
        
        Args:
            game_state: 游戏状态实例
        
        Returns:
            摸到的牌
        """
        if not game_state.deck:
            return None  # 牌墙已空
        
        return game_state.deck.pop()
    
    @staticmethod
    def discard_card(game_state, action) -> None:
        """将牌打入弃牌堆，记录完整来源信息"""
        game_state.discard_pile.append(action.card)
        game_state.last_discarded_card = action

    @staticmethod
    def draw_replacement(game_state, count: int = 3):
        """补牌：从牌墙随机取 count 张，选择其中一张入手，其余放回再洗"""
        deck = game_state.deck
        if not deck:
            return None

        draw_count = min(count, len(deck))
        pulled = [deck.pop() for _ in range(draw_count)]
        if not pulled:
            return None

        import random

        chosen = random.choice(pulled)
        # 未选中的牌放回并打乱，保持随机性
        remaining = [c for c in pulled if c is not chosen]
        deck.extend(remaining)
        random.shuffle(deck)
        return chosen

def shuffle_and_deal(game_state) -> None:
    """洗牌并发牌
    
    Args:
        game_state: 游戏状态实例
    """
    # 创建初始牌组
    initial_deck = DeckManager.create_initial_deck(game_state.rule)
    
    # 洗牌
    shuffled_deck = DeckManager.shuffle(initial_deck)
    
    # 设置到游戏状态中
    game_state.deck = shuffled_deck
    
    # 发牌
    DeckManager.deal(game_state)