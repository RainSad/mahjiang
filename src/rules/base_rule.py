class BaseRule:
    """规则基类，定义规则接口"""
    
    def __init__(self):
        # 通用规则配置
        self.max_players = 4
        self.tiles_count = 136
        self.starting_tiles = 13
        self.dealer_extra_tile = True
        self.allow_chow = True
        self.allow_pong = True
        self.allow_kong = True
        self.allow_self_hu = True
        self.allow_other_hu = True
    
    def can_chow(self, player: 'Player', card: 'Card', from_player) -> bool:
        """判断是否可以吃牌"""
        raise NotImplementedError
    
    def can_pong(self, player: 'Player', card: 'Card', from_player) -> bool:
        """判断是否可以碰牌"""
        raise NotImplementedError
    
    def can_kong(self, player: 'Player', card: 'Card', from_player) -> bool:
        """判断是否可以杠牌"""
        raise NotImplementedError
    
    def can_hu(self, player: 'Player', card: 'Card') -> bool:
        """判断是否可以胡牌"""
        raise NotImplementedError
    
    def calculate_score(self, player: 'Player', winning_card: 'Card') -> int:
        """计算胡牌分数"""
        raise NotImplementedError
    
    def get_valid_actions(self, player: 'Player', game_state: 'GameState') -> list:
        """获取当前玩家的有效操作"""
        raise NotImplementedError
    
    def create_initial_deck(self) -> list:
        """创建初始牌组"""
        raise NotImplementedError