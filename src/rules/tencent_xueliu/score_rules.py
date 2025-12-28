# /workspaces/mahjiang/src/rules/tencent_xueliu/score_rules.py
from collections import Counter
from src.core.data.card import Card


class TencentXueliuScoreRules:
    """血流成河麻将计分规则
    
    基础分：10分
    番型倍数：1-256倍
    根（杠）倍数：每根×2
    特殊倍数：自摸×4、杠上开花×4、杠上炮×4、抢杠胡×4、海底捞月×4
    """
    
    def __init__(self, rule):
        self.rule = rule
    
    def calculate_score(self, player, winning_card) -> int:
        """计算胡牌分数
        
        计分公式：
        基础分 × 番型倍数 × 根倍数 × 特殊倍数
        """
        base_score = 10
        
        # 计算番型倍数
        fan_multiplier = self._calculate_fans(player, winning_card)
        
        # 计算根（杠）倍数：每根×2
        gang_multiplier = self._calculate_gang_multiplier(player)
        
        # 计算特殊倍数
        special_multiplier = self._calculate_special_multiplier(player, winning_card)
        
        total_score = base_score * fan_multiplier * gang_multiplier * special_multiplier
        
        return int(total_score)
    
    def _calculate_fans(self, player, winning_card) -> int:
        """计算番型倍数
        
        按照从高到低检查番型，有些番型会覆盖低级番型
        """
        fans = 0
        
        # 256倍番型
        fans_256 = self._check_256_fans(player, winning_card)
        if fans_256 > 0:
            return fans_256
        
        # 128倍番型
        fans_128 = self._check_128_fans(player, winning_card)
        if fans_128 > 0:
            return fans_128
        
        # 32倍番型
        fans_32 = self._check_32_fans(player, winning_card)
        if fans_32 > 0:
            return fans_32
        
        # 16倍番型
        fans_16 = self._check_16_fans(player, winning_card)
        if fans_16 > 0:
            return fans_16
        
        # 8倍番型
        fans_8 = self._check_8_fans(player, winning_card)
        if fans_8 > 0:
            return fans_8
        
        # 4倍番型（可累加）
        fans += self._check_4_fans(player, winning_card)
        
        # 1倍番型（平胡）
        if fans == 0:
            fans = 1
        
        return min(fans, self.rule.max_fans)
    
    def _calculate_gang_multiplier(self, player) -> int:
        """计算杠的倍数：每根×2"""
        gang_count = self._gang_count(player)
        return 2 ** gang_count if gang_count > 0 else 1
    
    def _calculate_special_multiplier(self, player, winning_card) -> int:
        """计算特殊倍数
        
        自摸：×4
        杠上开花：×4
        杠上炮：×4
        抢杠胡：×4
        海底捞月：×4
        """
        multiplier = 1
        
        # 自摸
        if self._is_zi_mo(player, winning_card):
            multiplier *= 4
        
        # 杠上开花
        if self._is_gang_shang_kai_hua(player, winning_card):
            multiplier *= 4
        
        # 杠上炮
        if self._is_gang_shang_pao(player, winning_card):
            multiplier *= 4
        
        # 抢杠胡
        if self._is_qiang_gang_hu(player, winning_card):
            multiplier *= 4
        
        # 海底捞月
        if self._is_hai_di_lao_yue(player, winning_card):
            multiplier *= 4
        
        return multiplier
    
    # ========== 256倍番型 ==========
    def _check_256_fans(self, player, winning_card) -> int:
        """256倍番型：连七对
        
        限制：仅富商和尊爵场可胡
        """
        if self.rule.room_level not in ['富商场', '尊爵场']:
            return 0
        
        if self._is_lian_qi_dui(player):
            return 256
        
        return 0
    
    # ========== 128倍番型 ==========
    def _check_128_fans(self, player, winning_card) -> int:
        """128倍番型：九莲宝灯
        
        限制：仅富商和尊爵场可胡
        """
        if self.rule.room_level not in ['富商场', '尊爵场']:
            return 0
        
        if self._is_jiu_lian_bao_deng(player):
            return 128
        
        return 0
    
    # ========== 32倍番型 ==========
    def _check_32_fans(self, player, winning_card) -> int:
        """32倍番型：天胡、地胡、清十八罗汉、将十八罗汉"""
        
        # 天胡
        if self._is_tian_hu(player):
            return 32
        
        # 地胡
        if self._is_di_hu(player):
            return 32
        
        # 清十八罗汉
        if self._is_qing_shi_ba_luo_han(player):
            return 32
        
        # 将十八罗汉
        if self._is_jiang_shi_ba_luo_han(player):
            return 32
        
        return 0
    
    # ========== 16倍番型 ==========
    def _check_16_fans(self, player, winning_card) -> int:
        """16倍番型：清七对、清金钩钓、将七对、将金钩钓"""
        
        # 清七对
        if self._is_qing_qi_dui(player):
            return 16
        
        # 清金钩钓
        if self._is_qing_jin_gou_diao(player):
            return 16
        
        # 将七对
        if self._is_jiang_qi_dui(player):
            return 16
        
        # 将金钩钓
        if self._is_jiang_jin_gou_diao(player):
            return 16
        
        return 0
    
    # ========== 8倍番型 ==========
    def _check_8_fans(self, player, winning_card) -> int:
        """8倍番型：清碰、将对、十八罗汉"""
        
        # 清碰
        if self._is_qing_peng(player):
            return 8
        
        # 将对
        if self._is_jiang_dui(player):
            return 8
        
        # 十八罗汉
        if self._is_shi_ba_luo_han(player):
            return 8
        
        return 0
    
    # ========== 4倍番型（可累加） ==========
    def _check_4_fans(self, player, winning_card) -> int:
        """4倍番型（可累加）：清一色、七对、金钩钓、幺九、断幺九、碰碰胡、根、自摸、杠上开花、杠上炮、抢杠胡、海底捞月"""
        fans = 0
        
        # 清一色
        if self._is_qing_yi_se(player):
            fans += 4
        
        # 七对
        if self._is_qi_dui(player):
            fans += 4
        
        # 金钩钓
        if self._is_jin_gou_diao(player):
            fans += 4
        
        # 幺九
        if self._is_yao_jiu(player):
            fans += 4
        
        # 断幺九
        if self._is_duan_yao_jiu(player):
            fans += 4
        
        # 碰碰胡
        if self._is_peng_peng_hu(player):
            fans += 4
        
        # 根（通过杠倍数计算，这里不重复累加）
        
        # 自摸（通过特殊倍数计算，这里不重复累加）
        
        # 杠上开花（通过特殊倍数计算，这里不重复累加）
        
        # 杠上炮（通过特殊倍数计算，这里不重复累加）
        
        # 抢杠胡（通过特殊倍数计算，这里不重复累加）
        
        # 海底捞月（通过特殊倍数计算，这里不重复累加）
        
        return fans
    
    # ========== 番型判断 ==========
    
    def _is_lian_qi_dui(self, player) -> bool:
        """连七对：一种花色序数牌组成序数相连的7个对子"""
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        
        # 检查是否是七对
        if not self._is_qi_dui(player):
            return False
        
        # 检查是否是清一色
        suits = {t.suit for t in tiles}
        if len(suits) != 1 or list(suits)[0] not in ['万', '筒', '条']:
            return False
        
        # 检查序数是否连续
        ranks = sorted({int(t.rank) for t in tiles})
        if len(ranks) != 7:
            return False
        
        return ranks == list(range(ranks[0], ranks[0] + 7))
    
    def _is_jiu_lian_bao_deng(self, player) -> bool:
        """九莲宝灯：1112345678999 + 该花色任意一张牌"""
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        
        # 必须无碰杠
        if len(getattr(player, 'melds', [])) > 0:
            return False
        
        # 检查是否是清一色
        suits = {t.suit for t in tiles}
        if len(suits) != 1 or list(suits)[0] not in ['万', '筒', '条']:
            return False
        
        suit = list(suits)[0]
        counts = Counter(tiles)
        
        # 检查1和9是否至少有3张
        if counts[Card(suit, '1')] < 3 or counts[Card(suit, '9')] < 3:
            return False
        
        # 检查2-8是否至少有1张
        for r in ['2', '3', '4', '5', '6', '7', '8']:
            if counts[Card(suit, r)] < 1:
                return False
        
        return True
    
    def _is_tian_hu(self, player) -> bool:
        """天胡：庄家发完牌后立即胡牌"""
        return getattr(player, 'is_tian_hu', False)
    
    def _is_di_hu(self, player) -> bool:
        """地胡：非庄家第一轮摸牌就胡牌"""
        return getattr(player, 'is_di_hu', False)
    
    def _is_qing_shi_ba_luo_han(self, player) -> bool:
        """清十八罗汉：清一色+十八罗汉"""
        return self._is_qing_yi_se(player) and self._is_shi_ba_luo_han(player)
    
    def _is_jiang_shi_ba_luo_han(self, player) -> bool:
        """将十八罗汉：手牌全是2、5、8的十八罗汉"""
        if not self._is_shi_ba_luo_han(player):
            return False
        
        tiles = self._all_tiles(player)
        return all(t.suit in ['万', '筒', '条'] and t.rank in ['2', '5', '8'] for t in tiles)
    
    def _is_qing_qi_dui(self, player) -> bool:
        """清七对：清一色+七对"""
        return self._is_qing_yi_se(player) and self._is_qi_dui(player)
    
    def _is_qing_jin_gou_diao(self, player) -> bool:
        """清金钩钓：清一色+金钩钓"""
        return self._is_qing_yi_se(player) and self._is_jin_gou_diao(player)
    
    def _is_jiang_qi_dui(self, player) -> bool:
        """将七对：序数牌2、5、8组成的七对"""
        if not self._is_qi_dui(player):
            return False
        
        tiles = self._hand_only(player)
        return all(t.suit in ['万', '筒', '条'] and t.rank in ['2', '5', '8'] for t in tiles)
    
    def _is_jiang_jin_gou_diao(self, player) -> bool:
        """将金钩钓：手牌全是2、5、8的金钩钓"""
        if not self._is_jin_gou_diao(player):
            return False
        
        tiles = self._all_tiles(player)
        return all(t.suit in ['万', '筒', '条'] and t.rank in ['2', '5', '8'] for t in tiles)
    
    def _is_qing_peng(self, player) -> bool:
        """清碰：清一色+碰碰胡"""
        return self._is_qing_yi_se(player) and self._is_peng_peng_hu(player)
    
    def _is_jiang_dui(self, player) -> bool:
        """将对：手牌全是2、5、8的碰碰胡"""
        if not self._is_peng_peng_hu(player):
            return False
        
        tiles = self._all_tiles(player)
        return all(t.suit in ['万', '筒', '条'] and t.rank in ['2', '5', '8'] for t in tiles)
    
    def _is_shi_ba_luo_han(self, player) -> bool:
        """十八罗汉：金钩钓且胡牌时有4个杠牌"""
        return self._gang_count(player) == 4 and self._is_jin_gou_diao(player)
    
    def _is_qing_yi_se(self, player) -> bool:
        """清一色：全部由万/筒/条中某一种花色组成"""
        tiles = self._all_tiles(player)
        suits = {t.suit for t in tiles}
        return len(suits) == 1 and list(suits)[0] in ['万', '筒', '条']
    
    def _is_qi_dui(self, player) -> bool:
        """七对：由七个对子组成"""
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        
        counts = Counter(tiles)
        return all(v == 2 for v in counts.values()) and len(counts) == 7
    
    def _is_jin_gou_diao(self, player) -> bool:
        """金钩钓：胡牌时其他牌都被碰/杠，手牌只剩一张牌单钓"""
        hand = self._hand_only(player)
        melds = getattr(player, 'melds', [])
        return len(hand) == 2 and len(melds) == 4
    
    def _is_yao_jiu(self, player) -> bool:
        """幺九：每个刻子、顺子、将都包含1/9序数牌"""
        tiles = self._all_tiles(player)
        terminal = {t for t in tiles if t.suit in ['万', '筒', '条'] and t.rank in ['1', '9']}
        return len(terminal) > 0
    
    def _is_duan_yao_jiu(self, player) -> bool:
        """断幺九：手牌中没有1、9序数牌"""
        tiles = self._all_tiles(player)
        return all(t.suit in ['万', '筒', '条'] and 2 <= int(t.rank) <= 8 for t in tiles)
    
    def _is_peng_peng_hu(self, player) -> bool:
        """碰碰胡：由4个刻子（或杠牌）和将牌组成"""
        tiles = self._hand_only(player)
        counts = Counter(tiles)
        
        # 检查是否有一个对子（将牌）
        pair_count = sum(1 for v in counts.values() if v == 2)
        if pair_count != 1:
            return False
        
        # 检查其余牌是否都是刻子
        triplet_count = sum(1 for v in counts.values() if v == 3)
        meld_count = len(getattr(player, 'melds', []))
        
        return triplet_count + meld_count == 4
    
    # ========== 特殊胡牌判断 ==========
    
    def _is_zi_mo(self, player, winning_card) -> bool:
        """自摸：自摸胡牌"""
        return winning_card == getattr(player, 'drawn_card', None)
    
    def _is_gang_shang_kai_hua(self, player, winning_card) -> bool:
        """杠上开花：杠牌后补张自摸胡牌"""
        last_action = getattr(player, 'last_action', None)
        return last_action in ['明杠', '暗杠', '补杠', '杠牌'] and self._is_zi_mo(player, winning_card)
    
    def _is_gang_shang_pao(self, player, winning_card) -> bool:
        """杠上炮：杠牌后打出的牌让其他玩家点炮胡牌"""
        game_state = getattr(player, 'game_state', None)
        if not game_state:
            return False
        
        last_discarded_card = getattr(game_state, 'last_discarded_card', None)
        if not last_discarded_card:
            return False
        
        last_player = getattr(last_discarded_card, 'from_player', None)
        if not last_player:
            return False
        
        last_action = getattr(last_player, 'last_action', None)
        return last_action in ['明杠', '暗杠', '补杠', '杠牌'] and not self._is_zi_mo(player, winning_card)
    
    def _is_qiang_gang_hu(self, player, winning_card) -> bool:
        """抢杠胡：胡其他人补杠的那张牌"""
        game_state = getattr(player, 'game_state', None)
        if not game_state:
            return False
        
        last_discarded_card = getattr(game_state, 'last_discarded_card', None)
        if not last_discarded_card:
            return False
        
        last_player = getattr(last_discarded_card, 'from_player', None)
        if not last_player:
            return False
        
        last_action = getattr(last_player, 'last_action', None)
        return last_action == '补杠'
    
    def _is_hai_di_lao_yue(self, player, winning_card) -> bool:
        """海底捞月：摸到牌墙最后1张牌胡牌"""
        return getattr(player, 'is_last_card', False) and self._is_zi_mo(player, winning_card)
    
    # ========== 辅助方法 ==========
    
    def _all_tiles(self, player):
        """获取所有牌（手牌+面子牌）"""
        tiles = list(self._hand_only(player))
        for meld in getattr(player, 'melds', []):
            tiles.extend(getattr(meld, 'cards', []))
        return tiles
    
    def _hand_only(self, player):
        """仅获取手牌"""
        return list(getattr(player, 'hand', []))
    
    def _gang_count(self, player) -> int:
        """获取杠的数量（根）"""
        return sum(1 for m in getattr(player, 'melds', []) 
                  if getattr(m, 'type', '') in ['明杠', '暗杠', '补杠'])