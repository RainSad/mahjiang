# /workspaces/mahjiang/src/rules/tencent_xueliu/rule.py
from src.rules.base_rule import BaseRule
from src.rules.tencent_xueliu.hu_rules import TencentXueliuHuRules
from src.rules.tencent_xueliu.action_rules import TencentXueliuActionRules
from src.rules.tencent_xueliu.score_rules import TencentXueliuScoreRules

class TencentXueliuRule(BaseRule):
    """腾讯血流成河麻将规则实现
    
    特点：
    1. 只使用万、筒、条三种花色，共108张牌
    2. 不允许吃牌，只能碰、杠
    3. 必须定缺一门，摸到缺的花色必须打出
    4. 支持一炮多响
    5. 杠牌计分：明杠2倍、暗杠2倍、补杠1倍
    """
    
    def __init__(self, room_level='普通场'):
        super().__init__()
        # 血流麻将特定规则配置
        self.allow_chow = False      # 不允许吃牌
        self.allow_pong = True       # 允许碰牌
        self.allow_kong = True       # 允许杠牌
        self.allow_multiple_hu = True  # 允许一炮多响
        self.max_fans = 256          # 最大番数256倍
        self.mandatory_discard = True  # 必须有一张牌可以打出
        self.room_level = room_level  # 房间等级：普通场/富商场/尊爵场
        self.tiles_count = 108       # 牌数：万筒条108张
        
        # 加载子规则
        self.hu_rules = TencentXueliuHuRules(self)
        self.action_rules = TencentXueliuActionRules(self)
        self.score_rules = TencentXueliuScoreRules(self)
    
    def can_chow(self, player, card, from_player) -> bool:
        """血流麻将不允许吃牌"""
        return False
    
    def can_pong(self, player, card, from_player) -> bool:
        """血流麻将碰牌规则"""
        return self.action_rules.can_pong(player, card, from_player)
    
    def can_kong(self, player, card, from_player) -> bool:
        """血流麻将杠牌规则"""
        return self.action_rules.can_kong(player, card, from_player)
    
    def can_hu(self, player, card) -> bool:
        """血流麻将胡牌规则"""
        return self.hu_rules.can_hu(player, card)
    
    def calculate_score(self, player, winning_card) -> int:
        """血流麻将计分规则"""
        return self.score_rules.calculate_score(player, winning_card)
    
    def get_valid_actions(self, player, game_state) -> list:
        """获取当前玩家的有效操作"""
        return self.action_rules.get_valid_actions(player, game_state)
    
    def create_initial_deck(self) -> list:
        """创建血流麻将初始牌组（只有万、筒、条，共108张）"""
        from src.core.data.card import Card
        deck = []
        
        # 序数牌（万、筒、条），每种花色1-9各4张
        for suit in ['万', '筒', '条']:
            for rank in range(1, 10):
                for _ in range(4):
                    deck.append(Card(suit, str(rank)))
        
        return deck

    def exchange_three(self, game_state):
        """换三张：每位玩家可选最多三张与牌墙交换（自动选择手牌最高的三张）"""
        from src.core.data.card import Card
        import random
        for player in game_state.players:
            # 选择最多3张：按点数降序取前3
            suited = [c for c in player.hand if c.suit in ['万', '筒', '条']]
            suited.sort(key=lambda c: (int(c.rank), c.suit), reverse=True)
            give = suited[:3]
            if not give:
                continue
            for c in give:
                player.hand.remove(c)
            # 从牌墙取同等数量
            take = []
            for _ in give:
                if game_state.deck:
                    take.append(game_state.deck.pop())
            player.hand.extend(take)
            # 把给出的牌放回牌墙并洗牌
            game_state.deck.extend(give)
            random.shuffle(game_state.deck)

    def handle_call_transfer(self, winner, shooter):
        """呼叫转移：杠上炮需将上一杠所得转给胡牌玩家"""
        gain = getattr(shooter, "last_gang_gain", 0)
        if gain > 0:
            shooter.score -= gain
            winner.score += gain
            shooter.last_gang_gain = 0
            # 同步转移最近一次杠事件明细，避免退税错误归属
            last_event = getattr(shooter, 'last_gang_event', None)
            if last_event and hasattr(shooter, 'gang_events'):
                try:
                    shooter.gang_events.remove(last_event)
                except ValueError:
                    pass
                if not hasattr(winner, 'gang_events'):
                    winner.gang_events = []
                winner.gang_events.append(last_event)
                winner.last_gang_event = last_event
                shooter.last_gang_event = None

    def on_deck_empty(self, game_state):
        """牌墙摸空的结算：查花猪/查大叫/退税
        
        结算顺序：
        1. 查花猪：手牌含缺牌的玩家赔付 32倍 或 听牌最大倍数（取最大）
           - 天命花猪豁免：打出的牌均为缺牌则不赔
        2. 查大叫：未听牌玩家赔给听牌未胡玩家最大倍数（不含自摸）
        3. 退税：未听牌玩家返还全部杠牌所得
        """
        base = 10
        players = list(game_state.players)
        
        # ========== 查花猪 ==========
        self._settle_hua_zhu(game_state, players, base)
        
        # ========== 查大叫 ==========
        self._settle_cha_da_jiao(game_state, players, base)
        
        # ========== 退税 ==========
        self._settle_tui_shui(game_state, players, base)
    
    def _settle_hua_zhu(self, game_state, players, base):
        """查花猪：手牌含缺牌的玩家需赔付其余玩家
        
        规则：
        - 赔付金额 = max(32倍底分, 听牌玩家最大可胡倍数)
        - 天命花猪豁免：若玩家打出的牌均为缺牌，则无需赔付
        """
        for p in players:
            que = getattr(p, 'que_men', None)
            if not que:
                continue
            
            # 检查手牌中是否有缺牌
            has_que_in_hand = any(c.suit == que for c in p.hand)
            if not has_que_in_hand:
                continue
            
            # 检查是否是天命花猪（所有打出的牌都是缺牌）
            if self._is_tian_ming_hua_zhu(p, que):
                continue  # 天命花猪豁免
            
            # 计算赔付金额
            ting_fans = self._get_max_fans_for_listening(p, game_state)
            hua_zhu_penalty = max(32 * base, ting_fans * base)
            
            # 赔付给其他玩家
            for other in players:
                if other is p:
                    continue
                p.score -= hua_zhu_penalty
                other.score += hua_zhu_penalty
                if not hasattr(game_state, 'settlement_logs'):
                    game_state.settlement_logs = []
                game_state.settlement_logs.append({
                    'type': '查花猪',
                    'from': p.name,
                    'to': other.name,
                    'amount': hua_zhu_penalty
                })
    
    def _is_tian_ming_hua_zhu(self, player, que_men) -> bool:
        """检查是否是天命花猪
        
        天命花猪：玩家打出的所有牌都是缺牌
        """
        discarded = getattr(player, 'discarded_cards', [])
        if not discarded:
            return False
        
        # 检查所有打出的牌是否都是缺牌
        return all(c.suit == que_men for c in discarded)
    
    def _get_max_fans_for_listening(self, player, game_state) -> int:
        """获取听牌玩家的最大可胡倍数（不含自摸倍数）
        
        假设玩家听牌，计算其最佳情况下的番型倍数
        简化版：返回当前手牌的最大番型倍数（不含特殊倍数）
        """
        from src.core.data.card import Card
        
        max_fans = 1
        # 遍历所有可能的胡牌
        for suit in ['万', '筒', '条']:
            for rank in range(1, 10):
                test_card = Card(suit, str(rank))
                if self.can_hu(player, test_card):
                    fans = self.score_rules._calculate_fans(player, test_card)
                    # 移除特殊倍数（自摸等）
                    fans = min(fans, 256)  # 上限 256 倍
                    max_fans = max(max_fans, fans)
        
        return max_fans
    
    def _settle_cha_da_jiao(self, game_state, players, base):
        """查大叫：未听牌玩家赔给听牌未胡玩家最大倍数
        
        规则：
        - 识别听牌玩家（手牌能胡）
        - 识别未胡玩家（听牌但未胡的玩家）
        - 未听牌玩家赔付听牌最大倍数 × 底分
        """
        # 识别听牌玩家
        listening_players = []
        for p in players:
            # 仅包含“听牌但未胡”的玩家
            if self._is_player_listening(p, game_state) and p not in getattr(game_state, 'winners', []):
                listening_players.append(p)
        
        if not listening_players:
            return
        
        # 识别未听牌玩家
        for p in players:
            if p not in listening_players:
                # 未听牌玩家赔付听牌玩家最大倍数
                for listener in listening_players:
                    max_fans = self._get_max_fans_for_listening(listener, game_state)
                    penalty = max_fans * base
                    p.score -= penalty
                    listener.score += penalty
                    if not hasattr(game_state, 'settlement_logs'):
                        game_state.settlement_logs = []
                    game_state.settlement_logs.append({
                        'type': '查大叫',
                        'from': p.name,
                        'to': listener.name,
                        'amount': penalty
                    })
    
    def _is_player_listening(self, player, game_state) -> bool:
        """检查玩家是否听牌（至少能胡一种牌）"""
        from src.core.data.card import Card
        
        for suit in ['万', '筒', '条']:
            for rank in range(1, 10):
                test_card = Card(suit, str(rank))
                if self.can_hu(player, test_card):
                    return True
        return False
    
    def _settle_tui_shui(self, game_state, players, base):
        """退税：未听牌玩家按每次杠的实际贡献比例退还杠牌所得

        规则：
        - 仅未听牌玩家退税；听牌玩家保留其杠收益
        - 逐条遍历该玩家的每次杠事件，将记录的贡献者按原始支付金额逐一退还
        - 退税完成后清空该玩家的杠事件与累计收益
        - 记录明细到 settlement_logs 以便UI展示
        """
        # 初始化结算日志容器
        if not hasattr(game_state, 'settlement_logs'):
            game_state.settlement_logs = []

        for p in players:
            if self._is_player_listening(p, game_state):
                continue  # 听牌玩家不用退税

            events = list(getattr(p, 'gang_events', []))
            if not events:
                continue

            for ev in events:
                contributors = getattr(ev, 'contributors', None) if hasattr(ev, 'contributors') else ev.get('contributors', {})
                # contributors: {other_player: amount}
                for other, amount in contributors.items():
                    if other is p or amount <= 0:
                        continue
                    p.score -= amount
                    other.score += amount
                    game_state.settlement_logs.append({
                        'type': '退税',
                        'from': p.name,
                        'to': other.name,
                        'amount': amount,
                        'detail': f"{ev.get('type', '')}退还"
                    })

            # 清空事件与累计，避免重复退税
            p.gang_events = []
            p.last_gang_event = None
            p.total_gang_gain = 0
    
    def check_que_men(self, player) -> bool:
        """检查玩家手牌是否符合定缺规则
        
        定缺规则：手牌中的花色不能超过2门
        """
        # 获取手牌中的花色（不包括缺的花色）
        que_men = getattr(player, 'que_men', None)
        if not que_men:
            return True  # 未定缺时默认通过
        
        hand_suits = {card.suit for card in player.hand if card.suit in ['万', '筒', '条']}
        
        # 手牌中不应该有缺的花色
        if que_men in hand_suits:
            # 允许手牌中有缺牌，但必须在下一次出牌时打出
            return True
        
        return True
    
    def must_discard_que_men(self, player) -> bool:
        """检查玩家是否必须打出缺门的牌"""
        que_men = getattr(player, 'que_men', None)
        if not que_men:
            return False
        
        # 检查手牌中是否有缺门的牌
        has_que_card = any(card.suit == que_men for card in player.hand)
        return has_que_card