from collections import Counter, defaultdict
from itertools import combinations
from src.core.data.card import Card


class TencentScoreRules:
    """腾讯大众麻将计分规则（覆盖指定番型表）"""

    def __init__(self, rule):
        self.rule = rule

    # ========== 入口 ========== 
    def calculate_score(self, player, winning_card) -> int:
        base_score = 10
        fans_total = self._calculate_fans(player, winning_card)

        multiplier = 1
        if self._is_gang_shang_kai_hua(player, winning_card):
            multiplier *= 2
        if self._is_qiang_gang_hu(player, winning_card):
            multiplier *= 2
        if self._is_gang_shang_pao(player, winning_card):
            multiplier *= 2
        if self._is_miao_shou_hui_chun(player, winning_card):
            multiplier *= 2
        if self._is_hai_di_lao_yue(player, winning_card):
            multiplier *= 2
        if getattr(player, "is_dealer", False):
            multiplier *= 2
        if getattr(player, "consecutive_gang_count", 0) > 0:
            multiplier *= (player.consecutive_gang_count + 1)

        return fans_total * multiplier * base_score

    def _calculate_fans(self, player, winning_card) -> int:
        total = 0
        total += self._check_88_fans(player)
        total += self._check_64_fans(player)
        total += self._check_48_fans(player)
        total += self._check_36_fans(player)
        total += self._check_32_fans(player)
        total += self._check_24_fans(player)
        total += self._check_16_fans(player)
        total += self._check_12_fans(player)
        total += self._check_8_fans(player)
        total += self._check_4_fans(player)
        total += self._check_2_fans(player)
        total += self._check_1_fans(player, winning_card)
        return min(total, self.rule.max_fans)

    # ===================== 88 番 =====================
    def _check_88_fans(self, player) -> int:
        checks = [
            self._is_da_si_xi,
            self._is_da_san_yuan,
            self._is_shi_san_yao,
            self._is_tian_hu,
            self._is_di_hu,
            self._is_da_qi_xing,
            self._is_jiu_lian_bao_deng,
            self._is_shi_ba_luo_han,
            self._is_lian_qi_dui,
            self._is_lv_yi_se,
        ]
        return 88 if any(fn(player) for fn in checks) else 0

    # ===================== 64 番 =====================
    def _check_64_fans(self, player) -> int:
        fans = 0
        if self._is_xiao_si_xi(player):
            fans += 64
        if self._is_xiao_san_yuan(player):
            fans += 64
        if self._is_zi_yi_se(player):
            fans += 64
        if self._is_si_an_ke(player):
            fans += 64
        if self._is_yi_se_shuang_long_hui(player):
            fans += 64
        if self._is_qing_yao_jiu(player):
            fans += 64
        if self._is_ren_hu(player):
            fans += 64
        return fans

    # ===================== 48 番 =====================
    def _check_48_fans(self, player) -> int:
        fans = 0
        if self._is_si_tong_shun(player):
            fans += 48
        if self._is_si_lian_ke(player):
            fans += 48
        return fans

    # ===================== 36 番 =====================
    def _check_36_fans(self, player) -> int:
        fans = 0
        if self._is_yi_se_si_bu_gao(player):
            fans += 36
        if self._is_shi_er_jin_chai(player):
            fans += 36
        if self._is_hun_yao_jiu(player):
            fans += 36
        return fans

    # ===================== 32 番 =====================
    def _check_32_fans(self, player) -> int:
        fans = 0
        if self._is_seven_pairs(player):
            fans += 32
        if self._is_pure_suit(player):
            fans += 32
        if self._is_quan_shuang_ke(player):
            fans += 32
        if self._is_quan_da(player):
            fans += 32
        if self._is_quan_zhong(player):
            fans += 32
        if self._is_quan_xiao(player):
            fans += 32
        if self._is_san_lian_ke(player):
            fans += 32
        if self._is_san_tong_shun(player):
            fans += 32
        return fans

    # ===================== 24 番 =====================
    def _check_24_fans(self, player) -> int:
        fans = 0
        if self._is_qing_long(player):
            fans += 24
        if self._is_yi_se_san_bu_gao(player):
            fans += 24
        if self._is_san_tong_ke(player):
            fans += 24
        if self._is_san_an_ke(player):
            fans += 24
        if self._is_qi_xing_bu_kao(player):
            fans += 24
        return fans

    # ===================== 16 番 =====================
    def _check_16_fans(self, player) -> int:
        fans = 0
        if self._is_tui_bu_dao(player):
            fans += 16
        if self._is_chun_dai_yao_jiu(player):
            fans += 16
        if self._is_san_feng_ke(player):
            fans += 16
        if self._is_quan_dan(player):
            fans += 16
        return fans

    # ===================== 12 番 =====================
    def _check_12_fans(self, player) -> int:
        fans = 0
        if self._is_wu_men_qi(player):
            fans += 12
        if self._is_all_pairs(player):
            fans += 12
        if self._is_shuang_jian_ke(player):
            fans += 12
        if self._is_hua_long(player):
            fans += 12
        if self._is_zu_he_long(player):
            fans += 12
        if self._is_quan_bu_kao(player):
            fans += 12
        if self._is_san_se_san_tong_shun(player):
            fans += 12
        return fans

    # ===================== 8 番 =====================
    def _check_8_fans(self, player) -> int:
        fans = 0
        if self._is_jin_gou_diao(player):
            fans += 8
        if self._is_dai_yao_jiu(player):
            fans += 8
        if self._is_mixed_suit(player):
            fans += 8
        return fans

    # ===================== 4 番 =====================
    def _check_4_fans(self, player) -> int:
        fans = 0
        if self._is_duan_yao_jiu(player):
            fans += 4
        if self._is_yi_ban_gao(player):
            fans += 4
        if self._is_xi_xiang_feng(player):
            fans += 4
        if self._is_lian_liu(player):
            fans += 4
        if self._is_lao_shao_fu(player):
            fans += 4
        if self._is_jian_ke(player):
            fans += 4
        if self._is_chang_feng_ke(player):
            fans += 4
        if self._is_men_feng_ke(player):
            fans += 4
        if self._is_an_gang(player):
            fans += 4
        if self._is_si_gui_yi(player):
            fans += 4
        if self._is_men_qing(player):
            fans += 4
        if self._is_shuang_an_ke(player):
            fans += 4
        if self._is_shuang_tong_ke(player):
            fans += 4
        return fans

    # ===================== 2 番 =====================
    def _check_2_fans(self, player) -> int:
        fans = 0
        if self._is_si_hua(player):
            fans += 2
        if self._is_ming_gang(player):
            fans += 2
        return fans

    # ===================== 1 番 =====================
    def _check_1_fans(self, player, winning_card) -> int:
        fans = 0
        if self._is_zi_mo(player, winning_card):
            fans += 1
        return fans

    # ========== 88番判断 ==========
    def _is_da_si_xi(self, player) -> bool:
        return self._count_wind_ke(player) == 4

    def _is_da_san_yuan(self, player) -> bool:
        return self._count_arrow_ke(player) == 3

    def _is_shi_san_yao(self, player) -> bool:
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        required = [
            Card('万', '1'), Card('万', '9'),
            Card('筒', '1'), Card('筒', '9'),
            Card('条', '1'), Card('条', '9'),
            Card('风', '东'), Card('风', '南'), Card('风', '西'), Card('风', '北'),
            Card('箭', '中'), Card('箭', '发'), Card('箭', '白'),
        ]
        counts = Counter(tiles)
        if any(counts[c] == 0 for c in required):
            return False
        return any(counts[c] >= 2 for c in required)

    def _is_tian_hu(self, player) -> bool:
        return getattr(player, 'is_tian_hu', False)

    def _is_di_hu(self, player) -> bool:
        return getattr(player, 'is_di_hu', False)

    def _is_da_qi_xing(self, player) -> bool:
        tiles = self._hand_only(player)
        return self._is_seven_pairs(player) and all(c.suit in ['风', '箭'] for c in tiles)

    def _is_jiu_lian_bao_deng(self, player) -> bool:
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        suits = {t.suit for t in tiles}
        if len(suits) != 1 or list(suits)[0] not in ['万', '筒', '条']:
            return False
        suit = list(suits)[0]
        counts = Counter(tiles)
        pattern = {
            Card(suit, '1'): 3,
            Card(suit, '9'): 3,
        }
        if any(counts[c] < v for c, v in pattern.items()):
            return False
        for r in ['2', '3', '4', '5', '6', '7', '8']:
            if counts[Card(suit, r)] < 1:
                return False
        return True

    def _is_shi_ba_luo_han(self, player) -> bool:
        return self._gang_count(player) >= 4

    def _is_lian_qi_dui(self, player) -> bool:
        tiles = self._hand_only(player)
        if not self._is_seven_pairs(player):
            return False
        suits = {t.suit for t in tiles}
        if len(suits) != 1 or list(suits)[0] not in ['万', '筒', '条']:
            return False
        ranks = sorted({int(t.rank) for t in tiles})
        return ranks == list(range(ranks[0], ranks[0] + 7))

    def _is_lv_yi_se(self, player) -> bool:
        green = {
            Card('条', '2'), Card('条', '3'), Card('条', '4'),
            Card('条', '6'), Card('条', '8'), Card('箭', '发'),
        }
        return all(t in green for t in self._all_tiles(player))

    # ========== 64番判断 ==========
    def _is_xiao_si_xi(self, player) -> bool:
        wind_triplets = self._wind_triplet_detail(player)
        return len(wind_triplets) == 3 and self._has_pair(player, suit='风')

    def _is_xiao_san_yuan(self, player) -> bool:
        arrow_triplets = self._arrow_triplet_detail(player)
        return len(arrow_triplets) == 2 and self._has_pair(player, suit='箭')

    def _is_zi_yi_se(self, player) -> bool:
        return all(t.suit in ['风', '箭'] for t in self._all_tiles(player))

    def _is_si_an_ke(self, player) -> bool:
        return self._concealed_triplet_count(player) >= 4

    def _is_yi_se_shuang_long_hui(self, player) -> bool:
        tiles = self._all_tiles(player)
        suits = {t.suit for t in tiles}
        if len(suits) != 1 or list(suits)[0] not in ['万', '筒', '条']:
            return False
        suit = list(suits)[0]
        counts = Counter(tiles)
        cond_low = all(counts[Card(suit, r)] >= 1 for r in ['1', '2', '3'])
        cond_high = all(counts[Card(suit, r)] >= 1 for r in ['7', '8', '9'])
        cond_pair = counts[Card(suit, '5')] >= 2
        return cond_low and cond_high and cond_pair

    def _is_qing_yao_jiu(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and t.rank in ['1', '9'] for t in self._all_tiles(player))

    def _is_ren_hu(self, player) -> bool:
        return getattr(player, 'is_ren_hu', False)

    # ========== 48番判断 ==========
    def _is_si_tong_shun(self, player) -> bool:
        return self._sequence_multiplicity(player, needed=4)

    def _is_si_lian_ke(self, player) -> bool:
        return self._consecutive_triplets(player, length=4)

    # ========== 36番判断 ==========
    def _is_yi_se_si_bu_gao(self, player) -> bool:
        return self._step_sequences(player, length=4)

    def _is_shi_er_jin_chai(self, player) -> bool:
        return self._gang_count(player) >= 3

    def _is_hun_yao_jiu(self, player) -> bool:
        return all((t.suit in ['万', '筒', '条'] and t.rank in ['1', '9']) or t.suit in ['风', '箭'] for t in self._all_tiles(player))

    # ========== 32番判断 ==========
    def _is_seven_pairs(self, player) -> bool:
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        counts = Counter(tiles)
        return all(v == 2 for v in counts.values()) and len(counts) == 7

    def _is_pure_suit(self, player) -> bool:
        suits = {t.suit for t in self._all_tiles(player)}
        return len(suits) == 1 and list(suits)[0] in ['万', '筒', '条']

    def _is_quan_shuang_ke(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and int(t.rank) % 2 == 0 for t in self._all_tiles(player))

    def _is_quan_da(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and int(t.rank) >= 7 for t in self._all_tiles(player))

    def _is_quan_zhong(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and 4 <= int(t.rank) <= 6 for t in self._all_tiles(player))

    def _is_quan_xiao(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and int(t.rank) <= 3 for t in self._all_tiles(player))

    def _is_san_lian_ke(self, player) -> bool:
        return self._consecutive_triplets(player, length=3)

    def _is_san_tong_shun(self, player) -> bool:
        return self._sequence_multiplicity(player, needed=3)

    # ========== 24番判断 ==========
    def _is_qing_long(self, player) -> bool:
        tiles = self._all_tiles(player)
        suits = {t.suit for t in tiles if t.suit in ['万', '筒', '条']}
        if len(suits) != 1:
            return False
        suit = list(suits)[0]
        counts = Counter(tiles)
        return all(counts[Card(suit, str(r))] >= 1 for r in range(1, 10))

    def _is_yi_se_san_bu_gao(self, player) -> bool:
        return self._step_sequences(player, length=3)

    def _is_san_tong_ke(self, player) -> bool:
        tiles = self._all_tiles(player)
        triplets = self._all_triplet_ranks_by_rank(tiles)
        return any(len(suits) >= 3 for suits in triplets.values())

    def _is_san_an_ke(self, player) -> bool:
        return self._concealed_triplet_count(player) >= 3

    def _is_qi_xing_bu_kao(self, player) -> bool:
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        counts = Counter(tiles)
        if any(v > 1 for v in counts.values()):
            return False
        honor_set = {Card('风', r) for r in ['东', '南', '西', '北']} | {Card('箭', r) for r in ['中', '发', '白']}
        if not honor_set.issubset(set(tiles)):
            return False
        remaining = [t for t in tiles if t not in honor_set]
        if len(remaining) != 7:
            return False
        groups = [{1, 4, 7}, {2, 5, 8}, {3, 6, 9}]
        used_groups = set()
        for suit in ['万', '筒', '条']:
            suit_ranks = {int(t.rank) for t in remaining if t.suit == suit}
            if not suit_ranks:
                return False
            for idx, g in enumerate(groups):
                if suit_ranks.issubset(g):
                    used_groups.add(idx)
                    break
        return len(used_groups) == 3

    # ========== 16番判断 ==========
    def _is_tui_bu_dao(self, player) -> bool:
        allowed = {
            Card('筒', '2'), Card('筒', '4'), Card('筒', '5'), Card('筒', '6'), Card('筒', '8'), Card('筒', '9'),
            Card('条', '1'), Card('条', '2'), Card('条', '3'), Card('条', '4'), Card('条', '5'), Card('条', '8'), Card('条', '9'),
            Card('箭', '中'),
        }
        return all(t in allowed for t in self._all_tiles(player))

    def _is_chun_dai_yao_jiu(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and t.rank in ['1', '9'] for t in self._all_tiles(player))

    def _is_san_feng_ke(self, player) -> bool:
        return self._count_wind_ke(player) >= 3

    def _is_quan_dan(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and int(t.rank) % 2 == 1 for t in self._all_tiles(player))

    # ========== 12番判断 ==========
    def _is_wu_men_qi(self, player) -> bool:
        suits = {t.suit for t in self._all_tiles(player)}
        return {'万', '筒', '条', '风', '箭'}.issubset(suits)

    def _is_all_pairs(self, player) -> bool:
        tiles = self._all_tiles(player)
        counts = Counter(tiles)
        vals = sorted(counts.values())
        return vals == [2, 3, 3, 3, 3]

    def _is_shuang_jian_ke(self, player) -> bool:
        return self._count_arrow_ke(player) >= 2

    def _is_hua_long(self, player) -> bool:
        counts = Counter(self._all_tiles(player))
        for suits_perm in combinations(['万', '筒', '条'], 3):
            if all(counts[Card(suits_perm[0], r)] >= 1 for r in ['1', '2', '3']) and \
               all(counts[Card(suits_perm[1], r)] >= 1 for r in ['4', '5', '6']) and \
               all(counts[Card(suits_perm[2], r)] >= 1 for r in ['7', '8', '9']):
                return True
        return False

    def _is_zu_he_long(self, player) -> bool:
        counts = Counter(self._all_tiles(player))
        groups = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
        suits = ['万', '筒', '条']
        for perm in combinations(suits, 3):
            ok = True
            for suit, grp in zip(perm, groups):
                if not all(counts[Card(suit, str(r))] >= 1 for r in grp):
                    ok = False
                    break
            if ok:
                return True
        return False

    def _is_quan_bu_kao(self, player) -> bool:
        tiles = self._hand_only(player)
        if len(tiles) != 14:
            return False
        counts = Counter(tiles)
        if any(v > 1 for v in counts.values()):
            return False
        for suit in ['万', '筒', '条']:
            suit_ranks = sorted(int(t.rank) for t in tiles if t.suit == suit)
            for i in range(len(suit_ranks) - 2):
                if suit_ranks[i + 2] - suit_ranks[i] == 2 and suit_ranks[i + 1] - suit_ranks[i] == 1:
                    return False
        return True

    def _is_san_se_san_tong_shun(self, player) -> bool:
        counts = Counter(self._all_tiles(player))
        for start in range(1, 8):
            need = [str(start), str(start + 1), str(start + 2)]
            if all(all(counts[Card(suit, r)] >= 1 for r in need) for suit in ['万', '筒', '条']):
                return True
        return False

    # ========== 8番判断 ==========
    def _is_jin_gou_diao(self, player) -> bool:
        return len(self._hand_only(player)) == 1 and len(getattr(player, 'melds', [])) == 4

    def _is_dai_yao_jiu(self, player) -> bool:
        tiles = self._all_tiles(player)
        terminal_or_honor = {t for t in tiles if (t.suit in ['万', '筒', '条'] and t.rank in ['1', '9']) or t.suit in ['风', '箭']}
        return len(terminal_or_honor) > 0 and len(terminal_or_honor) < len(tiles)

    def _is_mixed_suit(self, player) -> bool:
        suits = {t.suit for t in self._all_tiles(player)}
        return len(suits) == 2 and bool({'万', '筒', '条'}.intersection(suits)) and bool({'风', '箭'}.intersection(suits))

    # ========== 4番判断 ==========
    def _is_duan_yao_jiu(self, player) -> bool:
        return all(t.suit in ['万', '筒', '条'] and 2 <= int(t.rank) <= 8 for t in self._all_tiles(player))

    def _is_yi_ban_gao(self, player) -> bool:
        return self._sequence_multiplicity(player, needed=2)

    def _is_xi_xiang_feng(self, player) -> bool:
        counts = Counter(self._all_tiles(player))
        for start in range(1, 8):
            need = [str(start), str(start + 1), str(start + 2)]
            suits_with_seq = 0
            for suit in ['万', '筒', '条']:
                if all(counts[Card(suit, r)] >= 1 for r in need):
                    suits_with_seq += 1
            if suits_with_seq >= 2:
                return True
        return False

    def _is_lian_liu(self, player) -> bool:
        counts = Counter(self._all_tiles(player))
        for suit in ['万', '筒', '条']:
            for start in range(1, 5):
                if all(counts[Card(suit, str(r))] >= 1 for r in range(start, start + 6)):
                    return True
        return False

    def _is_lao_shao_fu(self, player) -> bool:
        counts = Counter(self._all_tiles(player))
        for suit in ['万', '筒', '条']:
            if all(counts[Card(suit, r)] >= 1 for r in ['1', '2', '3']) and all(counts[Card(suit, r)] >= 1 for r in ['7', '8', '9']):
                return True
        return False

    def _is_jian_ke(self, player) -> bool:
        return self._count_arrow_ke(player) >= 1

    def _is_chang_feng_ke(self, player) -> bool:
        wind = getattr(player, 'chang_feng', None)
        if not wind:
            return False
        return self._has_ke(player, Card('风', wind))

    def _is_men_feng_ke(self, player) -> bool:
        wind = getattr(player, 'men_feng', None)
        if not wind:
            return False
        return self._has_ke(player, Card('风', wind))

    def _is_an_gang(self, player) -> bool:
        return any(getattr(m, 'type', '') == '暗杠' for m in getattr(player, 'melds', []))

    def _is_si_gui_yi(self, player) -> bool:
        counts = Counter(self._hand_only(player))
        return any(v >= 4 for v in counts.values())

    def _is_men_qing(self, player) -> bool:
        melds = getattr(player, 'melds', [])
        if not melds:
            return True
        exposed = {'明刻', '明杠', '吃', '碰', '杠'}
        return not any(getattr(m, 'type', '') in exposed for m in melds)

    def _is_shuang_an_ke(self, player) -> bool:
        return self._concealed_triplet_count(player) >= 2

    def _is_shuang_tong_ke(self, player) -> bool:
        tiles = self._all_tiles(player)
        triplets = self._all_triplet_ranks_by_rank(tiles)
        return any(len(suits) >= 2 for suits in triplets.values())

    # ========== 2番判断 ==========
    def _is_si_hua(self, player) -> bool:
        if hasattr(player, 'huapai_count'):
            return player.huapai_count >= 4
        return len(getattr(player, 'hua_cards', [])) >= 4

    def _is_ming_gang(self, player) -> bool:
        return any(getattr(m, 'type', '') == '明杠' for m in getattr(player, 'melds', []))

    # ========== 1番判断 ==========
    def _is_zi_mo(self, player, winning_card) -> bool:
        return self._is_self_draw(player, winning_card)

    def _is_yao_jiu_ke(self, player, winning_card=None, require_self_draw: bool = False) -> bool:
        if require_self_draw and not self._is_self_draw(player, winning_card):
            return False
        counts = Counter(self._all_tiles(player))
        for suit in ['万', '筒', '条']:
            if counts[Card(suit, '1')] >= 3 or counts[Card(suit, '9')] >= 3:
                return True
        return False

    # ========== 翻倍 ==========
    def _is_gang_shang_kai_hua(self, player, winning_card) -> bool:
        return getattr(player, 'last_action', None) in ['明杠', '暗杠', '补杠', '补花', '杠牌'] and self._is_self_draw(player, winning_card)

    def _is_miao_shou_hui_chun(self, player, winning_card) -> bool:
        return getattr(player, 'is_last_card', False) and self._is_self_draw(player, winning_card)

    def _is_hai_di_lao_yue(self, player, winning_card) -> bool:
        return getattr(player, 'is_last_card', False) and not self._is_self_draw(player, winning_card)

    def _is_qiang_gang_hu(self, player, winning_card) -> bool:
        game_state = getattr(player, 'game_state', None)
        if game_state and getattr(game_state, 'last_discarded_card', None):
            last_card = game_state.last_discarded_card.card
            last_player = game_state.last_discarded_card.from_player
            return winning_card == last_card and getattr(last_player, 'last_action', None) == '补杠'
        return False

    def _is_gang_shang_pao(self, player, winning_card) -> bool:
        game_state = getattr(player, 'game_state', None)
        if game_state and getattr(game_state, 'last_discarded_card', None):
            last_card = game_state.last_discarded_card.card
            last_player = game_state.last_discarded_card.from_player
            return winning_card == last_card and getattr(last_player, 'last_action', None) in ['明杠', '暗杠', '补杠', '杠牌']
        return False

    # ========== 辅助 ==========
    def _all_tiles(self, player):
        tiles = list(self._hand_only(player))
        for meld in getattr(player, 'melds', []):
            tiles.extend(getattr(meld, 'cards', []))
        return [t for t in tiles if t.suit != '花']

    def _hand_only(self, player):
        return [t for t in getattr(player, 'hand', []) if t.suit != '花']

    def _gang_count(self, player) -> int:
        return sum(1 for m in getattr(player, 'melds', []) if getattr(m, 'type', '') in ['明杠', '暗杠'])

    def _count_wind_ke(self, player) -> int:
        wind = ['东', '南', '西', '北']
        return sum(1 for r in wind if self._has_ke(player, Card('风', r)))

    def _count_arrow_ke(self, player) -> int:
        arrows = ['中', '发', '白']
        return sum(1 for r in arrows if self._has_ke(player, Card('箭', r)))

    def _wind_triplet_detail(self, player):
        return {r for r in ['东', '南', '西', '北'] if self._has_ke(player, Card('风', r))}

    def _arrow_triplet_detail(self, player):
        return {r for r in ['中', '发', '白'] if self._has_ke(player, Card('箭', r))}

    def _has_ke(self, player, card) -> bool:
        count_hand = sum(1 for c in self._hand_only(player) if c == card)
        if count_hand >= 3:
            return True
        for meld in getattr(player, 'melds', []):
            if getattr(meld, 'type', '') in ['明刻', '暗刻', '明杠', '暗杠'] and any(c == card for c in getattr(meld, 'cards', [])):
                return True
        return False

    def _has_pair(self, player, suit=None):
        counts = Counter(self._hand_only(player))
        for card, v in counts.items():
            if v >= 2 and (suit is None or card.suit == suit):
                return True
        return False

    def _concealed_triplet_count(self, player) -> int:
        count = 0
        counts = Counter(self._hand_only(player))
        count += sum(1 for v in counts.values() if v >= 3)
        count += sum(1 for m in getattr(player, 'melds', []) if getattr(m, 'type', '') in ['暗刻', '暗杠'])
        return count

    def _all_triplet_ranks_by_rank(self, tiles):
        counts = Counter(tiles)
        ranks = defaultdict(set)
        for card, v in counts.items():
            if v >= 3:
                ranks[card.rank].add(card.suit)
        return ranks

    def _is_self_draw(self, player, winning_card) -> bool:
        if winning_card == getattr(player, 'drawn_card', None):
            return True
        return getattr(player, 'last_action', None) in ['明杠', '暗杠', '补杠', '补花', '杠牌']

    def _sequence_multiplicity(self, player, needed: int) -> bool:
        counts = Counter(self._all_tiles(player))
        for suit in ['万', '筒', '条']:
            for start in range(1, 8):
                if min(counts[Card(suit, str(start + i))] for i in range(3)) >= needed:
                    return True
        return False

    def _consecutive_triplets(self, player, length: int) -> bool:
        counts = Counter(self._all_tiles(player))
        for suit in ['万', '筒', '条']:
            for start in range(1, 10 - length):
                if all(counts[Card(suit, str(start + i))] >= 3 for i in range(length)):
                    return True
        return False

    def _step_sequences(self, player, length: int) -> bool:
        counts = Counter(self._all_tiles(player))
        for suit in ['万', '筒', '条']:
            starts = [s for s in range(1, 8) if all(counts[Card(suit, str(s + i))] >= 1 for i in range(3))]
            starts.sort()
            for combo in combinations(starts, length):
                if not all(combo[i + 1] - combo[i] in [1, 2] for i in range(len(combo) - 1)):
                    continue
                need = Counter()
                for start in combo:
                    for offset in range(3):
                        need[Card(suit, str(start + offset))] += 1
                if all(counts[tile] >= req for tile, req in need.items()):
                    return True
        return False
