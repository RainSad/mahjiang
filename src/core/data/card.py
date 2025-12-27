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
    
    def get_display_name(self):
        """获取牌的显示名称
        
        Returns:
            str: 牌的显示名称
        """
        suit_names = {
            '万': '万',
            '筒': '筒',
            '条': '条',
            '风': '',
            '箭': '',
            '花': ''
        }
        return f"{self.rank}{suit_names.get(self.suit, '')}"
    
    def __lt__(self, other):
        """定义小于比较运算符，用于排序
        
        Args:
            other: 另一个Card对象
        
        Returns:
            bool: 当前对象是否小于另一个对象
        """
        # 花色优先级：万 < 筒 < 条 < 风 < 箭 < 花
        suit_order = {'万': 0, '筒': 1, '条': 2, '风': 3, '箭': 4, '花': 5}
        
        # 风牌优先级：东 < 南 < 西 < 北
        wind_order = {'东': 0, '南': 1, '西': 2, '北': 3}
        
        # 箭牌优先级：中 < 发 < 白
        arrow_order = {'中': 0, '发': 1, '白': 2}
        
        # 花牌优先级：梅 < 兰 < 竹 < 菊 < 春 < 夏 < 秋 < 冬
        flower_order = {'梅': 0, '兰': 1, '竹': 2, '菊': 3, '春': 4, '夏': 5, '秋': 6, '冬': 7}
        
        # 先比较花色
        if suit_order[self.suit] != suit_order[other.suit]:
            return suit_order[self.suit] < suit_order[other.suit]
        
        # 同花色，比较点数
        if self.suit in ['万', '筒', '条']:
            return int(self.rank) < int(other.rank)
        elif self.suit == '风':
            return wind_order[self.rank] < wind_order[other.rank]
        elif self.suit == '箭':
            return arrow_order[self.rank] < arrow_order[other.rank]
        elif self.suit == '花':
            return flower_order[self.rank] < flower_order[other.rank]
        
        # 其他情况，默认返回False
        return False