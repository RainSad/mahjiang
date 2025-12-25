from collections import Counter, defaultdict
from src.core.data.card import Card

class TencentScoreRules:
    """腾讯大众麻将计分规则"""
    
    def __init__(self, rule):
        self.rule = rule
    
    def calculate_score(self, player, winning_card) -> int:
        """计算胡牌分数
        
        Args:
            player: 胡牌玩家
            winning_card: 胡牌的牌
        
        Returns:
            胡牌分数
        """
        # 基础分数
        base_score = 1
        
        # 计算番数
        fans = self._calculate_fans(player, winning_card)
        
        # 计算最终分数（基础分 × 2^番数）
        final_score = base_score * (2 ** fans)
        
        return final_score
    
    def _calculate_fans(self, player, winning_card) -> int:
        """计算番数
        
        Args:
            player: 胡牌玩家
            winning_card: 胡牌的牌
        
        Returns:
            番数（最大不超过规则设定的max_fans）
        """
        total_fans = 0
        
        # 88番
        total_fans += self._check_88_fans(player, winning_card)
        
        # 64番
        total_fans += self._check_64_fans(player)
        
        # 48番
        total_fans += self._check_48_fans(player)
        
        # 36番
        total_fans += self._check_36_fans(player)
        
        # 32番
        total_fans += self._check_32_fans(player)
        
        # 24番
        total_fans += self._check_24_fans(player)
        
        # 16番
        total_fans += self._check_16_fans(player)
        
        # 12番
        total_fans += self._check_12_fans(player)
        
        # 8番
        total_fans += self._check_8_fans(player)
        
        # 4番
        total_fans += self._check_4_fans(player, winning_card)
        
        # 2番
        total_fans += self._check_2_fans(player)
        
        # 1番
        total_fans += self._check_1_fans(player, winning_card)
        
        # 翻倍番型
        total_fans = self._check_double_fans(player, winning_card, total_fans)
        
        # 限制最大番数
        return min(total_fans, self.rule.max_fans)
    
    def _check_88_fans(self, player, winning_card) -> int:
        """检查88番番型"""
        fans = 0
        
        # 大四喜
        if self._is_da_si_xi(player):
            return 88
        
        # 大三元
        if self._is_da_san_yuan(player):
            return 88
        
        # 十三幺
        if self._is_shi_san_yao(player, winning_card):
            return 88
        
        # 天胡
        if self._is_tian_hu(player, winning_card):
            return 88
        
        # 地胡
        if self._is_di_hu(player, winning_card):
            return 88
        
        # 大七星
        if self._is_da_qi_xing(player):
            return 88
        
        # 九莲宝灯
        if self._is_jiu_lian_bao_deng(player):
            return 88
        
        # 十八罗汉
        if self._is_shi_ba_luo_han(player):
            return 88
        
        # 连七对
        if self._is_lian_qi_dui(player):
            return 88
        
        # 绿一色
        if self._is_lv_yi_se(player):
            return 88
        
        return fans
    
    def _check_64_fans(self, player) -> int:
        """检查64番番型"""
        fans = 0
        
        # 小四喜
        if self._is_xiao_si_xi(player):
            return 64
        
        # 小三元
        if self._is_xiao_san_yuan(player):
            return 64
        
        # 字一色
        if self._is_zi_yi_se(player):
            return 64
        
        # 四暗刻
        if self._is_si_an_ke(player):
            return 64
        
        # 一色双龙会
        if self._is_yi_se_shuang_long_hui(player):
            return 64
        
        # 清幺九
        if self._is_qing_yao_jiu(player):
            return 64
        
        # 人胡
        if self._is_ren_hu(player):
            return 64
        
        return fans
    
    def _check_48_fans(self, player) -> int:
        """检查48番番型"""
        fans = 0
        
        # 四同顺
        if self._is_si_tong_shun(player):
            return 48
        
        # 四连刻
        if self._is_si_lian_ke(player):
            return 48
        
        return fans
    
    def _check_36_fans(self, player) -> int:
        """检查36番番型"""
        fans = 0
        
        # 一色四步高
        if self._is_yi_se_si_bu_gao(player):
            return 36
        
        # 十二金钗
        if self._is_shi_er_jin_chai(player):
            return 36
        
        # 混幺九
        if self._is_hun_yao_jiu(player):
            return 36
        
        return fans
    
    def _check_32_fans(self, player) -> int:
        """检查32番番型"""
        fans = 0
        
        # 七对
        if self._is_seven_pairs(player):
            fans += 32
        
        # 清一色
        if self._is_pure_suit(player):
            fans += 32
        
        # 全双刻
        if self._is_quan_shuang_ke(player):
            fans += 32
        
        # 全大
        if self._is_quan_da(player):
            fans += 32
        
        # 全中
        if self._is_quan_zhong(player):
            fans += 32
        
        # 全小
        if self._is_quan_xiao(player):
            fans += 32
        
        # 三连刻
        if self._is_san_lian_ke(player):
            fans += 32
        
        # 三同顺
        if self._is_san_tong_shun(player):
            fans += 32
        
        return fans
    
    def _check_24_fans(self, player) -> int:
        """检查24番番型"""
        fans = 0
        
        # 清龙
        if self._is_qing_long(player):
            fans += 24
        
        # 一色三步高
        if self._is_yi_se_san_bu_gao(player):
            fans += 24
        
        # 三同刻
        if self._is_san_tong_ke(player):
            fans += 24
        
        # 三暗刻
        if self._is_san_an_ke(player):
            fans += 24
        
        # 七星不靠
        if self._is_qi_xing_bu_kao(player):
            fans += 24
        
        return fans
    
    def _check_16_fans(self, player) -> int:
        """检查16番番型"""
        fans = 0
        
        # 推不倒
        if self._is_tui_bu_dao(player):
            fans += 16
        
        # 纯带幺九
        if self._is_chun_dai_yao_jiu(player):
            fans += 16
        
        # 三风刻
        if self._is_san_feng_ke(player):
            fans += 16
        
        # 全单
        if self._is_quan_dan(player):
            fans += 16
        
        # 三色双龙会
        if self._is_san_se_shuang_long_hui(player):
            fans += 16
        
        # 双暗杠
        if self._is_shuang_an_gang(player):
            fans += 16
        
        # 双箭刻
        if self._is_shuang_jian_ke(player):
            fans += 16
        
        return fans
    
    def _check_12_fans(self, player) -> int:
        """检查12番番型"""
        fans = 0
        
        # 五门齐
        if self._is_wu_men_qi(player):
            fans += 12
        
        # 碰碰胡
        if self._is_all_pairs(player):
            fans += 12
        
        # 双箭刻
        if self._is_shuang_jian_ke(player):
            fans += 12
        
        # 花龙
        if self._is_hua_long(player):
            fans += 12
        
        # 组合龙
        if self._is_zu_he_long(player):
            fans += 12
        
        # 全不靠
        if self._is_quan_bu_kao(player):
            fans += 12
        
        # 三色三同顺
        if self._is_san_se_san_tong_shun(player):
            fans += 12
        
        return fans
    
    def _check_8_fans(self, player) -> int:
        """检查8番番型"""
        fans = 0
        
        # 金钩钓
        if self._is_jin_gou_diao(player):
            fans += 8
        
        # 带幺九
        if self._is_dai_yao_jiu(player):
            fans += 8
        
        # 混一色
        if self._is_mixed_suit(player):
            fans += 8
        
        # 花龙
        if self._is_hua_long(player):
            fans += 8
        
        # 三色三同顺
        if self._is_san_se_san_tong_shun(player):
            fans += 8
        
        # 三色三节高
        if self._is_san_se_san_jie_gao(player):
            fans += 8
        
        # 全双刻
        if self._is_quan_shuang_ke(player):
            fans += 8
        
        # 三暗刻
        if self._is_san_an_ke(player):
            fans += 8
        
        return fans
    
    def _check_4_fans(self, player, winning_card) -> int:
        """检查4番番型"""
        fans = 0
        
        # 断幺九
        if self._is_duan_yao_jiu(player):
            fans += 4
        
        # 一般高
        if self._is_yi_ban_gao(player):
            fans += 4
        
        # 喜相逢
        if self._is_xi_xiang_feng(player):
            fans += 4
        
        # 连六
        if self._is_lian_liu(player):
            fans += 4
        
        # 老少副
        if self._is_lao_shao_fu(player):
            fans += 4
        
        # 箭刻
        if self._is_jian_ke(player):
            fans += 4
        
        # 场风刻
        if self._is_chang_feng_ke(player):
            fans += 4
        
        # 门风刻
        if self._is_men_feng_ke(player):
            fans += 4
        
        # 暗杠
        if self._is_an_gang(player):
            fans += 4
        
        # 四归一
        if self._is_si_gui_yi(player):
            fans += 4
        
        # 门清
        if self._is_men_qing(player):
            fans += 4
        
        # 双暗刻
        if self._is_shuang_an_ke(player):
            fans += 4
        
        # 双同刻
        if self._is_shuang_tong_ke(player):
            fans += 4
        
        return fans
    
    def _check_2_fans(self, player) -> int:
        """检查2番番型"""
        fans = 0
        
        # 四花
        if self._is_si_hua(player):
            fans += 2
        
        # 明杠
        if self._is_ming_gang(player):
            fans += 2
        
        return fans
    
    def _check_1_fans(self, player, winning_card) -> int:
        """检查1番番型"""
        fans = 0
        
        # 自摸
        if self._is_zi_mo(player, winning_card):
            fans += 1
        
        return fans
    
    def _check_double_fans(self, player, winning_card, total_fans) -> int:
        """检查翻倍番型"""
        # 杠上开花
        if self._is_gang_shang_kai_hua(player, winning_card):
            return total_fans * 2
        
        # 妙手回春
        if self._is_miao_shou_hui_chun(player, winning_card):
            return total_fans * 2
        
        # 海底捞月
        if self._is_hai_di_lao_yue(player, winning_card):
            return total_fans * 2
        
        # 抢杠胡
        if self._is_qiang_gang_hu(player, winning_card):
            return total_fans * 2
        
        # 杠上炮
        if self._is_gang_shang_pao(player, winning_card):
            return total_fans * 2
        
        return total_fans
    
    # 番型检查方法实现
    def _is_da_si_xi(self, player) -> bool:
        """判断是否是大四喜"""
        # 大四喜：4副风刻（杠）组成的胡牌
        wind_counts = self._count_wind_ke(player)
        return wind_counts == 4
    
    def _is_da_san_yuan(self, player) -> bool:
        """判断是否是大三元"""
        # 大三元：胡牌中含有中、发、白3副刻子
        arrow_counts = self._count_arrow_ke(player)
        return arrow_counts == 3
    
    def _is_shi_san_yao(self, player, winning_card) -> bool:
        """判断是否是十三幺"""
        # 十三幺：由3种序数牌的一、九牌，七种字牌及其中一对作将组成的胡牌
        if len(player.hand) != 14:
            return False
        
        # 收集所有必要的牌
        required_cards = set()
        
        # 3种序数牌的一、九牌
        for suit in ['万', '筒', '条']:
            required_cards.add(Card(suit, '1'))
            required_cards.add(Card(suit, '9'))
        
        # 七种字牌
        for wind in ['东', '南', '西', '北']:
            required_cards.add(Card('风', wind))
        for arrow in ['中', '发', '白']:
            required_cards.add(Card('箭', arrow))
        
        # 检查手牌是否包含所有必要的牌，且最多有一个对子

        card_counts = Counter(player.hand)
        
        # 检查是否包含所有必要的牌
        if not all(any(card.id == rc.id for card in player.hand) for rc in required_cards):
            return False
        
        # 检查是否只有一个对子，其余都是单张
        pair_count = 0
        for count in card_counts.values():
            if count == 2:
                pair_count += 1
            elif count > 2:
                return False
        
        return pair_count == 1
    
    def _is_tian_hu(self, player, winning_card) -> bool:
        """判断是否是天胡"""
        # 天胡：庄家在发完牌后直接胡牌
        # 需要游戏状态支持
        return False
    
    def _is_lian_liu(self, player) -> bool:
        """判断是否是连六"""
        # 连六：胡牌时有3种花色6张连续序数牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有序数牌
        ordinal_cards = []
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                ordinal_cards.append((card.suit, int(card.rank)))
        
        if len(ordinal_cards) < 6:
            return False
        
        # 按点数排序
        ordinal_cards.sort(key=lambda x: x[1])
        
        # 检查是否有6张连续的序数牌
        for i in range(len(ordinal_cards) - 5):
            # 检查是否连续
            is_consecutive = True
            for j in range(5):
                if ordinal_cards[i+j][1] + 1 != ordinal_cards[i+j+1][1]:
                    is_consecutive = False
                    break
            
            if is_consecutive:
                # 检查是否包含3种花色
                suits = {card[0] for card in ordinal_cards[i:i+6]}
                if len(suits) == 3:
                    return True
        
        return False
    
    def _is_lao_shao_fu(self, player) -> bool:
        """判断是否是老少副"""
        # 老少副：胡牌时某一种花色123和789的顺子各一副
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查每种花色是否有123和789的顺子
        for suit in ['万', '筒', '条']:
            # 检查手牌中是否有该花色的123和789顺子
            has_low_straight = False
            has_high_straight = False
            
            # 检查手牌
    
            hand_counts = Counter(player.hand)
            
            # 检查123顺子
            if hand_counts.get(Card(suit, '1'), 0) >= 1 and \
               hand_counts.get(Card(suit, '2'), 0) >= 1 and \
               hand_counts.get(Card(suit, '3'), 0) >= 1:
                has_low_straight = True
            
            # 检查789顺子
            if hand_counts.get(Card(suit, '7'), 0) >= 1 and \
               hand_counts.get(Card(suit, '8'), 0) >= 1 and \
               hand_counts.get(Card(suit, '9'), 0) >= 1:
                has_high_straight = True
            
            # 检查吃碰杠
            if hasattr(player, 'melds'):
                for meld in player.melds:
                    if meld.type == '吃':
                        cards = meld.cards
                        cards.sort(key=lambda x: int(x.rank))
                        if cards[0].suit == suit:
                            # 检查是否是123顺子
                            if cards[0].rank == '1' and cards[1].rank == '2' and cards[2].rank == '3':
                                has_low_straight = True
                            # 检查是否是789顺子
                            elif cards[0].rank == '7' and cards[1].rank == '8' and cards[2].rank == '9':
                                has_high_straight = True
            
            # 如果该花色同时有123和789顺子，则满足条件
            if has_low_straight and has_high_straight:
                return True
        
        return False
    
    def _is_jian_ke(self, player) -> bool:
        """判断是否是箭刻"""
        # 箭刻：胡牌时有1副箭牌的刻子
        return self._count_arrow_ke(player) >= 1
    
    def _is_chang_feng_ke(self, player) -> bool:
        """判断是否是场风刻"""
        # 场风刻：胡牌时有场风的刻子
        if not hasattr(player, 'chang_feng'):
            return False
        

        hand_counts = Counter(player.hand)
        
        # 检查手牌中是否有场风刻子
        if hand_counts.get(Card('风', player.chang_feng), 0) >= 3:
            return True
        
        # 检查吃碰杠中是否有场风刻子
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                    card = meld.cards[0]
                    if card.suit == '风' and card.rank == player.chang_feng:
                        return True
        
        return False
    
    def _is_men_feng_ke(self, player) -> bool:
        """判断是否是门风刻"""
        # 门风刻：胡牌时有门风的刻子
        if not hasattr(player, 'men_feng'):
            return False
        

        hand_counts = Counter(player.hand)
        
        # 检查手牌中是否有门风刻子
        if hand_counts.get(Card('风', player.men_feng), 0) >= 3:
            return True
        
        # 检查吃碰杠中是否有门风刻子
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                    card = meld.cards[0]
                    if card.suit == '风' and card.rank == player.men_feng:
                        return True
        
        return False
    
    def _is_an_gang(self, player) -> bool:
        """判断是否是暗杠"""
        # 暗杠：胡牌时有1个暗杠
        if not hasattr(player, 'melds'):
            return False
        
        return any(meld.type == '暗杠' for meld in player.melds)
    
    def _is_si_gui_yi(self, player) -> bool:
        """判断是否是四归一"""
        # 四归一：胡牌时有4张相同的牌归到一副牌中（包括杠牌）

        hand_counts = Counter(player.hand)
        
        # 检查手牌中是否有4张相同的牌
        if any(count >= 4 for count in hand_counts.values()):
            return True
        
        # 检查吃碰杠中是否有4张相同的牌
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type in ['明杠', '暗杠']:
                    return True
        
        return False
    
    def _is_men_qing(self, player) -> bool:
        """判断是否是门清"""
        # 门清：胡牌时没有吃、碰、明杠，暗杠不算
        if not hasattr(player, 'melds'):
            return True
        
        return all(meld.type in ['暗杠'] for meld in player.melds)
    
    def _is_shuang_an_ke(self, player) -> bool:
        """判断是否是双暗刻"""
        # 双暗刻：胡牌时有2个暗刻
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type in ['暗刻', '暗杠']]) == 2
    
    def _is_shuang_tong_ke(self, player) -> bool:
        """判断是否是双同刻"""
        # 双同刻：胡牌时有2副花色不同、点数相同的刻子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有刻子
        triplets = []
        
        # 检查手牌中的刻子

        hand_counts = Counter(player.hand)
        for card, count in hand_counts.items():
            if count >= 3:
                triplets.append((card.suit, int(card.rank)))
        
        # 检查吃碰杠中的刻子
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                    card = meld.cards[0]
                    triplets.append((card.suit, int(card.rank)))
        
        # 检查是否有相同点数的刻子
        from collections import defaultdict
        rank_to_suits = defaultdict(set)
        for suit, rank in triplets:
            rank_to_suits[rank].add(suit)
        
        # 检查是否有相同点数但花色不同的刻子
        for suits in rank_to_suits.values():
            if len(suits) >= 2:
                return True
        
        return False
    
    def _is_si_hua(self, player) -> bool:
        """判断是否是四花"""
        # 四花：胡牌时有4张花牌
        if not hasattr(player, 'hua_cards'):
            return False
        
        return len(player.hua_cards) == 4
    
    def _is_ming_gang(self, player) -> bool:
        """判断是否是明杠"""
        # 明杠：胡牌时有1个明杠
        if not hasattr(player, 'melds'):
            return False
        
        return any(meld.type == '明杠' for meld in player.melds)
    
    def _is_zi_mo(self, player, winning_card) -> bool:
        """判断是否是自摸"""
        # 自摸：胡牌时通过自己摸牌胡牌
        if not hasattr(player, 'is_zi_mo'):
            return False
        
        return player.is_zi_mo
    
    def _is_di_hu(self, player, winning_card) -> bool:
        """判断是否是地胡"""
        # 地胡：非庄家在第一轮摸牌后立即自摸胡牌
        # 需要游戏状态支持
        return False
    
    def _is_da_qi_xing(self, player) -> bool:
        """判断是否是大七星"""
        # 大七星：由七种字牌组成的七对
        return self._is_seven_pairs(player) and all(c.suit in ['风', '箭'] for c in player.hand)
    
    def _is_jiu_lian_bao_deng(self, player) -> bool:
        """判断是否是九莲宝灯"""
        # 九莲宝灯：一种花色的1112345678999牌型
        if len(player.hand) != 14:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        # 统计每种牌的数量

        card_counts = Counter(card.rank for card in player.hand)
        
        # 检查是否是1112345678999的牌型
        required_counts = {
            '1': 3,
            '2': 1,
            '3': 1,
            '4': 1,
            '5': 1,
            '6': 1,
            '7': 1,
            '8': 1,
            '9': 3
        }
        
        # 允许有一个牌多一张（作为将牌）
        for rank, count in required_counts.items():
            if rank not in card_counts or card_counts[rank] < count:
                return False
        
        # 检查总牌数是否正确
        total_count = sum(card_counts.values())
        return total_count == 14
    
    def _is_shi_ba_luo_han(self, player) -> bool:
        """判断是否是十八罗汉"""
        # 十八罗汉：胡牌时手中有4副杠牌
        return len([m for m in player.melds if m.type in ['明杠', '暗杠']]) == 4
    
    def _is_lian_qi_dui(self, player) -> bool:
        """判断是否是连七对"""
        # 连七对：由同一花色序数牌组成的序数相连的7个对子
        if not self._is_seven_pairs(player):
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        # 获取所有不同的牌
        unique_cards = list(set(player.hand))
        
        # 按点数排序
        unique_cards.sort(key=lambda x: int(x.rank))
        
        # 检查是否是连续的7个点数
        if len(unique_cards) != 7:
            return False
        
        return (int(unique_cards[0].rank) + 1 == int(unique_cards[1].rank) and
                int(unique_cards[1].rank) + 1 == int(unique_cards[2].rank) and
                int(unique_cards[2].rank) + 1 == int(unique_cards[3].rank) and
                int(unique_cards[3].rank) + 1 == int(unique_cards[4].rank) and
                int(unique_cards[4].rank) + 1 == int(unique_cards[5].rank) and
                int(unique_cards[5].rank) + 1 == int(unique_cards[6].rank))
    
    def _is_lv_yi_se(self, player) -> bool:
        """判断是否是绿一色"""
        # 绿一色：由2、3、4、6、8条及发财组成的胡牌
        green_cards = {'条2', '条3', '条4', '条6', '条8', '箭发'}
        return all(c.suit + c.rank in green_cards for c in player.hand)
    
    def _is_xiao_si_xi(self, player) -> bool:
        """判断是否是小四喜"""
        # 小四喜：胡牌时有风牌的3副刻子及1对将牌
        wind_counts = self._count_wind_ke(player)
        return wind_counts == 3 and self._has_wind_pair(player)
    
    def _is_xiao_san_yuan(self, player) -> bool:
        """判断是否是小三元"""
        # 小三元：胡牌时有箭牌的2副刻子及1对将牌
        arrow_counts = self._count_arrow_ke(player)
        return arrow_counts == 2 and self._has_arrow_pair(player)
    
    def _is_zi_yi_se(self, player) -> bool:
        """判断是否是字一色"""
        # 字一色：由字牌的刻子（杠）、将组成的胡牌
        return all(c.suit in ['风', '箭'] for c in player.hand)
    
    def _is_si_an_ke(self, player) -> bool:
        """判断是否是四暗刻"""
        # 四暗刻：4个暗刻（暗杠）组成的胡牌
        return len([m for m in player.melds if m.type in ['暗刻', '暗杠']]) == 4
    
    def _is_yi_se_shuang_long_hui(self, player) -> bool:
        """判断是否是一色双龙会"""
        # 一色双龙会：一种花色的两个老少副，5为将牌
        if len(player.hand) != 14:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        # 统计每种牌的数量

        card_counts = Counter(card.rank for card in player.hand)
        
        # 检查是否有两个123顺子和两个789顺子，以及一个5的对子
        if card_counts.get('1', 0) < 2 or card_counts.get('2', 0) < 2 or card_counts.get('3', 0) < 2:
            return False
        if card_counts.get('7', 0) < 2 or card_counts.get('8', 0) < 2 or card_counts.get('9', 0) < 2:
            return False
        if card_counts.get('5', 0) != 2:
            return False
        
        # 检查是否只有这些牌
        required_ranks = {'1', '2', '3', '5', '7', '8', '9'}
        if not set(card_counts.keys()).issubset(required_ranks):
            return False
        
        return True
    
    def _is_qing_yao_jiu(self, player) -> bool:
        """判断是否是清幺九"""
        # 清幺九：只由序数牌一、九组成的胡牌
        return all(c.suit in ['万', '筒', '条'] and c.rank in ['1', '9'] for c in player.hand)
    
    def _is_ren_hu(self, player) -> bool:
        """判断是否是人胡"""
        # 人胡：非庄家发完牌后第一轮就吃胡
        # 需要游戏状态支持
        return False
    
    def _is_si_tong_shun(self, player) -> bool:
        """判断是否是四同顺"""
        # 四同顺：一种花色4副相同点数的顺子（如123、123、123、123）
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有序数牌
        from collections import defaultdict
        suit_cards = defaultdict(list)
        
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_cards[card.suit].append(int(card.rank))
        
        # 检查每种花色
        for suit, ranks in suit_cards.items():
            if len(ranks) < 12:
                continue
                
            # 统计每种点数的数量
    
            rank_counts = Counter(ranks)
            
            # 四同顺需要有4副相同的顺子，例如123需要1、2、3各4张
            for i in range(1, 8):  # 顺子可能是123到789
                if (rank_counts.get(i, 0) >= 4 and
                    rank_counts.get(i+1, 0) >= 4 and
                    rank_counts.get(i+2, 0) >= 4):
                    return True
        
        return False
    
    def _is_si_lian_ke(self, player) -> bool:
        """判断是否是四连刻"""
        # 四连刻：一种花色4副依次递增一位数的刻子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有刻子
        ke_ranks = []
        
        # 检查手牌中的刻子

        card_counts = Counter(player.hand)
        for card, count in card_counts.items():
            if card.suit in ['万', '筒', '条'] and count >= 3:
                ke_ranks.append((card.suit, int(card.rank)))
        
        # 检查明刻、暗刻、明杠、暗杠
        for meld in player.melds:
            if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                card = meld.cards[0]
                if card.suit in ['万', '筒', '条']:
                    ke_ranks.append((card.suit, int(card.rank)))
        
        # 检查是否有4副连刻
        if len(ke_ranks) < 4:
            return False
        
        # 按花色和点数排序
        ke_ranks.sort()
        
        # 检查是否有连续的4个刻子
        for i in range(len(ke_ranks) - 3):
            # 检查是否是同一花色
            if (ke_ranks[i][0] == ke_ranks[i+1][0] == 
                ke_ranks[i+2][0] == ke_ranks[i+3][0]):
                # 检查是否是连续的点数
                if (ke_ranks[i][1] + 1 == ke_ranks[i+1][1] and
                    ke_ranks[i+1][1] + 1 == ke_ranks[i+2][1] and
                    ke_ranks[i+2][1] + 1 == ke_ranks[i+3][1]):
                    return True
        
        return False
    
    def _is_yi_se_si_bu_gao(self, player) -> bool:
        """判断是否是一色四步高"""
        # 一色四步高：一种花色4副依次递增一位数或二位数的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        suit = next(iter(suits))
        
        # 收集所有该花色的牌
        cards = [card for card in player.hand if card.suit == suit]
        if len(cards) < 12:  # 4副顺子需要12张牌
            return False
        
        # 按点数排序
        cards.sort(key=lambda x: int(x.rank))
        ranks = [int(card.rank) for card in cards]
        
        # 收集所有不同的点数
        unique_ranks = sorted(list(set(ranks)))
        
        # 检查是否有4副依次递增一位数或二位数的顺子
        # 遍历所有可能的起始点
        for i in range(len(unique_ranks) - 3):
            start = unique_ranks[i]
            for j in range(i + 1, len(unique_ranks) - 2):
                second = unique_ranks[j]
                # 第二个顺子比起始顺子高1或2位
                if second - start not in [1, 2]:
                    continue
                for k in range(j + 1, len(unique_ranks) - 1):
                    third = unique_ranks[k]
                    # 第三个顺子比第二个顺子高1或2位
                    if third - second not in [1, 2]:
                        continue
                    for l in range(k + 1, len(unique_ranks)):
                        fourth = unique_ranks[l]
                        # 第四个顺子比第三个顺子高1或2位
                        if fourth - third not in [1, 2]:
                            continue
                        
                        # 检查是否有足够的牌组成这四个顺子
                        if (ranks.count(start) >= 1 and ranks.count(start + 1) >= 1 and ranks.count(start + 2) >= 1 and
                            ranks.count(second) >= 1 and ranks.count(second + 1) >= 1 and ranks.count(second + 2) >= 1 and
                            ranks.count(third) >= 1 and ranks.count(third + 1) >= 1 and ranks.count(third + 2) >= 1 and
                            ranks.count(fourth) >= 1 and ranks.count(fourth + 1) >= 1 and ranks.count(fourth + 2) >= 1):
                            return True
        
        return False
    
    def _is_shi_er_jin_chai(self, player) -> bool:
        """判断是否是十二金钗"""
        # 十二金钗：胡牌时手中有3副杠牌
        return len([m for m in player.melds if m.type in ['明杠', '暗杠']]) == 3
    
    def _is_hun_yao_jiu(self, player) -> bool:
        """判断是否是混幺九"""
        # 混幺九：由序数牌一、九和字牌组成的胡牌
        return all(c.suit in ['风', '箭'] or (c.suit in ['万', '筒', '条'] and c.rank in ['1', '9']) for c in player.hand)
    
    def _is_quan_shuang_ke(self, player) -> bool:
        """判断是否是全双刻"""
        # 全双刻：胡牌时手牌都是双数的序数牌
        return all(c.suit in ['万', '筒', '条'] and int(c.rank) % 2 == 0 for c in player.hand)
    
    def _is_quan_da(self, player) -> bool:
        """判断是否是全大"""
        # 全大：胡牌时手牌都是七、八、九的序数牌
        return all(c.suit in ['万', '筒', '条'] and int(c.rank) >= 7 for c in player.hand)
    
    def _is_quan_zhong(self, player) -> bool:
        """判断是否是全中"""
        # 全中：胡牌时手牌都是四、五、六的序数牌
        return all(c.suit in ['万', '筒', '条'] and 4 <= int(c.rank) <= 6 for c in player.hand)
    
    def _is_quan_xiao(self, player) -> bool:
        """判断是否是全小"""
        # 全小：胡牌时手牌都是一、二、三的序数牌
        return all(c.suit in ['万', '筒', '条'] and int(c.rank) <= 3 for c in player.hand)
    
    def _is_san_lian_ke(self, player) -> bool:
        """判断是否是三连刻"""
        # 三连刻：一种花色3副依次递增一位数字的刻子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有刻子
        ke_ranks = []
        
        # 检查手牌中的刻子

        card_counts = Counter(player.hand)
        for card, count in card_counts.items():
            if card.suit in ['万', '筒', '条'] and count >= 3:
                ke_ranks.append((card.suit, int(card.rank)))
        
        # 检查明刻、暗刻、明杠、暗杠
        for meld in player.melds:
            if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                card = meld.cards[0]
                if card.suit in ['万', '筒', '条']:
                    ke_ranks.append((card.suit, int(card.rank)))
        
        # 检查是否有3副连刻
        if len(ke_ranks) < 3:
            return False
        
        # 按花色和点数排序
        ke_ranks.sort()
        
        # 检查是否有连续的3个刻子
        for i in range(len(ke_ranks) - 2):
            # 检查是否是同一花色
            if (ke_ranks[i][0] == ke_ranks[i+1][0] == 
                ke_ranks[i+2][0]):
                # 检查是否是连续的点数
                if (ke_ranks[i][1] + 1 == ke_ranks[i+1][1] and
                    ke_ranks[i+1][1] + 1 == ke_ranks[i+2][1]):
                    return True
        
        return False
    
    def _is_san_tong_shun(self, player) -> bool:
        """判断是否是三同顺"""
        # 三同顺：一种花色3副序数相同的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有序数牌
        from collections import defaultdict
        suit_cards = defaultdict(list)
        
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_cards[card.suit].append(card)
        
        # 检查每种花色是否有3副相同的顺子
        for suit, cards in suit_cards.items():
            if len(cards) < 9:  # 3副顺子需要9张牌
                continue
            
            # 统计每个点数的数量
    
            rank_counts = Counter(card.rank for card in cards)
            
            # 检查是否有3副相同的顺子
            for rank in ['1', '2', '3', '4', '5', '6', '7']:
                # 检查是否有足够的点数组成3副顺子
                if (rank_counts.get(rank, 0) >= 3 and 
                    rank_counts.get(str(int(rank) + 1), 0) >= 3 and 
                    rank_counts.get(str(int(rank) + 2), 0) >= 3):
                    return True
        
        return False
    
    def _is_qing_long(self, player) -> bool:
        """判断是否是清龙"""
        # 清龙：一种花色1-9相连的序数牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        # 检查是否包含1-9的所有点数
        ranks = set(int(card.rank) for card in player.hand)
        return set(range(1, 10)).issubset(ranks)
    
    def _is_yi_se_san_bu_gao(self, player) -> bool:
        """判断是否是一色三步高"""
        # 一色三步高：一种花色3副依次递增一位数或二位数的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        suit = next(iter(suits))
        
        # 收集所有该花色的牌
        cards = [card for card in player.hand if card.suit == suit]
        if len(cards) < 9:  # 3副顺子需要9张牌
            return False
        
        # 按点数排序
        cards.sort(key=lambda x: int(x.rank))
        ranks = [int(card.rank) for card in cards]
        
        # 收集所有不同的点数
        unique_ranks = sorted(list(set(ranks)))
        
        # 检查是否有3副依次递增一位数或二位数的顺子
        # 遍历所有可能的起始点
        for i in range(len(unique_ranks) - 2):
            start = unique_ranks[i]
            for j in range(i + 1, len(unique_ranks) - 1):
                middle = unique_ranks[j]
                for k in range(j + 1, len(unique_ranks)):
                    end = unique_ranks[k]
                    
                    # 检查是否形成三步高
                    # 中间的顺子比起始顺子高1或2位
                    # 最后的顺子比中间顺子高1或2位
                    if ((middle - start == 1 or middle - start == 2) and 
                        (end - middle == 1 or end - middle == 2)):
                        
                        # 检查是否有足够的牌组成这三个顺子
                        if (ranks.count(start) >= 1 and ranks.count(start + 1) >= 1 and ranks.count(start + 2) >= 1 and
                            ranks.count(middle) >= 1 and ranks.count(middle + 1) >= 1 and ranks.count(middle + 2) >= 1 and
                            ranks.count(end) >= 1 and ranks.count(end + 1) >= 1 and ranks.count(end + 2) >= 1):
                            return True
        
        return False
    
    def _is_san_tong_ke(self, player) -> bool:
        """判断是否是三同刻"""
        # 三同刻：3个序数相同的刻子（杠）
        # 收集所有刻子和杠子的序数
        ke_ranks = []
        
        # 检查手牌中的刻子

        card_counts = Counter(player.hand)
        for card, count in card_counts.items():
            if card.suit in ['万', '筒', '条'] and count >= 3:
                ke_ranks.append(card.rank)
        
        # 检查明刻、暗刻、明杠、暗杠
        for meld in player.melds:
            if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                card = meld.cards[0]
                if card.suit in ['万', '筒', '条']:
                    ke_ranks.append(card.rank)
        
        # 检查是否有3个相同的序数

        rank_counts = Counter(ke_ranks)
        return any(count >= 3 for count in rank_counts.values())
    
    def _is_san_an_ke(self, player) -> bool:
        """判断是否是三暗刻"""
        # 三暗刻：胡牌时包含3个暗刻
        return len([m for m in player.melds if m.type in ['暗刻', '暗杠']]) == 3
    
    def _is_qi_xing_bu_kao(self, player) -> bool:
        """判断是否是七星不靠"""
        # 七星不靠：有7个单张的东南西北中发白，加3种花色按147、258、369组合的牌
        if len(player.hand) != 14:
            return False
        
        # 检查是否有7个单张的东南西北中发白
        required_word_cards = {'东', '南', '西', '北', '中', '发', '白'}
        found_word_cards = set()
        
        # 收集字牌和序数牌
        word_cards = []
        suit_cards = []
        
        for card in player.hand:
            if card.suit == '风' and card.rank in required_word_cards:
                word_cards.append(card)
                found_word_cards.add(card.rank)
            elif card.suit == '箭' and card.rank in required_word_cards:
                word_cards.append(card)
                found_word_cards.add(card.rank)
            elif card.suit in ['万', '筒', '条']:
                suit_cards.append(card)
        
        # 检查是否有7个单张的东南西北中发白
        if len(found_word_cards) != 7 or len(word_cards) != 7:
            return False
        
        # 检查是否有3种花色
        suits = set(card.suit for card in suit_cards)
        if len(suits) != 3 or not {'万', '筒', '条'}.issubset(suits):
            return False
        
        # 检查剩余的7张牌是否是3种花色按147、258、369组合的牌
        allowed_groups = [
            {1, 4, 7},  # 147组
            {2, 5, 8},  # 258组
            {3, 6, 9}   # 369组
        ]
        
        # 检查每种花色的牌是否在同一个组
        from collections import defaultdict
        suit_ranks = defaultdict(list)
        
        for card in suit_cards:
            suit_ranks[card.suit].append(int(card.rank))
        
        for suit, ranks in suit_ranks.items():
            # 检查是否有重复的序数牌
            if len(set(ranks)) != len(ranks):
                return False
            
            # 检查是否所有牌都在同一个组
            in_group = False
            for group in allowed_groups:
                if set(ranks).issubset(group):
                    in_group = True
                    break
            
            if not in_group:
                return False
        
        return True
    
    def _is_tui_bu_dao(self, player) -> bool:
        """判断是否是推不倒"""
        # 推不倒：由牌面图形无上下区别的牌组成的胡牌
        # 推不倒的牌包括：
        # 筒子：2, 4, 5, 6, 8, 9
        # 条子：1, 2, 3, 4, 5, 8, 9
        # 字牌：中
        for card in player.hand:
            if card.suit == '筒':
                if card.rank not in ['2', '4', '5', '6', '8', '9']:
                    return False
            elif card.suit == '条':
                if card.rank not in ['1', '2', '3', '4', '5', '8', '9']:
                    return False
            elif card.suit == '箭' and card.rank == '中':
                continue
            elif card.suit in ['万', '风', '箭']:
                # 万子、其他字牌和箭牌（除中）都不符合要求
                return False
        
        return True
    
    def _is_chun_dai_yao_jiu(self, player) -> bool:
        """判断是否是纯带幺九"""
        # 纯带幺九：胡牌时每副牌、将牌都包含一或九的序数牌
        return all(c.suit in ['万', '筒', '条'] and c.rank in ['1', '9'] for c in player.hand)
    
    def _is_san_feng_ke(self, player) -> bool:
        """判断是否是三风刻"""
        # 三风刻：胡牌时包含3副风刻
        return self._count_wind_ke(player) == 3
    
    def _is_quan_dan(self, player) -> bool:
        """判断是否是全单"""
        # 全单：胡牌时手牌都是单数的序数牌
        return all(c.suit in ['万', '筒', '条'] and int(c.rank) % 2 == 1 for c in player.hand)
    
    def _is_wu_men_qi(self, player) -> bool:
        """判断是否是五门齐"""
        # 五门齐：胡牌时3种序数牌、风、箭牌齐全
        suits = {c.suit for c in player.hand}
        return len(suits) == 5 and '万' in suits and '筒' in suits and '条' in suits and '风' in suits and '箭' in suits
    
    def _is_shuang_jian_ke(self, player) -> bool:
        """判断是否是双箭刻"""
        # 双箭刻：胡牌时有2副箭刻（或杠）
        return self._count_arrow_ke(player) == 2
    
    def _is_shuang_an_gang(self, player) -> bool:
        """判断是否是双暗杠"""
        # 双暗杠：胡牌时有2个暗杠
        if not hasattr(player, 'melds'):
            return False
        
        dark_gang_count = 0
        for meld in player.melds:
            if meld.type == '暗杠':
                dark_gang_count += 1
        
        return dark_gang_count == 2
    
    def _is_san_se_shuang_long_hui(self, player) -> bool:
        """判断是否是三色双龙会"""
        # 三色双龙会：胡牌时有3种花色的2副顺子，每种花色的顺子连接成1-9的序数牌，且相同的顺子排列
        # 例如：万123、万789，筒123、筒789，条123、条789
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否包含三种花色
        suits = set(card.suit for card in player.hand)
        if not {'万', '筒', '条'}.issubset(suits):
            return False
        
        # 收集所有序数牌
        ordinal_cards = {}
        for suit in ['万', '筒', '条']:
            ordinal_cards[suit] = []
            for card in player.hand:
                if card.suit == suit:
                    ordinal_cards[suit].append(int(card.rank))
        
        # 检查每种花色是否都有123和789的顺子
        for suit, ranks in ordinal_cards.items():
            if 1 not in ranks or 2 not in ranks or 3 not in ranks:
                return False
            if 7 not in ranks or 8 not in ranks or 9 not in ranks:
                return False
        
        return True
    
    def _is_hua_long(self, player) -> bool:
        """判断是否是花龙"""
        # 花龙：3种花色的3副顺子连接成1-9的序数牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否包含三种花色
        suits = set(card.suit for card in player.hand)
        if not {'万', '筒', '条'}.issubset(suits):
            return False
        
        # 检查是否包含1-3、4-6、7-9的顺子
        from collections import defaultdict
        suit_ranks = defaultdict(list)
        
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_ranks[card.suit].append(int(card.rank))
        
        # 检查每种花色是否有不同的顺子段
        segments = []
        for ranks in suit_ranks.values():
            if not ranks:
                continue
            
            # 检查是否有1-3的顺子
            if all(r in ranks for r in [1, 2, 3]):
                segments.append('low')
            # 检查是否有4-6的顺子
            elif all(r in ranks for r in [4, 5, 6]):
                segments.append('mid')
            # 检查是否有7-9的顺子
            elif all(r in ranks for r in [7, 8, 9]):
                segments.append('high')
        
        # 花龙需要包含low、mid、high三个不同的顺子段
        return set(segments) == {'low', 'mid', 'high'}
    
    def _is_zu_he_long(self, player) -> bool:
        """判断是否是组合龙"""
        # 组合龙：包含3种花色的147、258、369的9张序数牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否包含三种花色
        suits = set(card.suit for card in player.hand)
        if not {'万', '筒', '条'}.issubset(suits):
            return False
        
        # 检查是否包含组合龙的牌型
        dragon_patterns = [
            [1, 4, 7],  # 147
            [2, 5, 8],  # 258
            [3, 6, 9]   # 369
        ]
        
        from collections import defaultdict
        suit_ranks = defaultdict(set)
        
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_ranks[card.suit].add(int(card.rank))
        
        # 检查每种花色是否对应一个龙的模式
        found_patterns = []
        for suit, ranks in suit_ranks.items():
            for i, pattern in enumerate(dragon_patterns):
                if set(pattern).issubset(ranks):
                    found_patterns.append(i)
                    break
        
        # 组合龙需要包含三种不同的龙模式
        return len(set(found_patterns)) == 3
    
    def _is_quan_bu_kao(self, player) -> bool:
        """判断是否是全不靠"""
        # 全不靠：由单张3种花色的147、258、369序数牌及字牌中任意14张组成
        if len(player.hand) != 14:
            return False
        
        # 全不靠的牌型要求：
        # 1. 所有牌都是单张（没有对子、刻子等）
        # 2. 序数牌必须是147、258、369的组合
        # 3. 没有相同花色的牌在同一组（如万1和万4不能同时存在）
        
        from collections import defaultdict
        suit_ranks = defaultdict(list)
        word_cards = []
        
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_ranks[card.suit].append(int(card.rank))
            else:
                word_cards.append(card)
        
        # 检查是否有重复的字牌
        if len(set(word_cards)) != len(word_cards):
            return False
        
        # 检查序数牌是否符合要求
        allowed_groups = [
            {1, 4, 7},  # 147组
            {2, 5, 8},  # 258组
            {3, 6, 9}   # 369组
        ]
        
        for suit, ranks in suit_ranks.items():
            # 检查是否有重复的序数牌
            if len(set(ranks)) != len(ranks):
                return False
            
            # 检查是否所有牌都在同一个组
            in_group = False
            for group in allowed_groups:
                if set(ranks).issubset(group):
                    in_group = True
                    break
            
            if not in_group:
                return False
        
        return True
    
    def _is_yi_ban_gao(self, player) -> bool:
        """判断是否是一般高"""
        # 一般高：胡牌时有2副花色相同、序数相同的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有顺子
        straights = []
        
        # 检查手牌中的顺子

        hand_counts = Counter(player.hand)
        
        # 检查手牌中是否有2副相同的顺子
        for card, count in hand_counts.items():
            if card.suit in ['万', '筒', '条'] and count >= 2:
                # 检查是否有相同的顺子
                next_rank = str(int(card.rank) + 1)
                next_next_rank = str(int(card.rank) + 2)
                
                if hand_counts.get(Card(card.suit, next_rank), 0) >= 2 and \
                   hand_counts.get(Card(card.suit, next_next_rank), 0) >= 2:
                    return True
        
        # 检查吃碰杠中的顺子
        if hasattr(player, 'melds'):
            meld_straights = []
            for meld in player.melds:
                if meld.type == '吃':
                    # 记录顺子的花色和起始点数
                    cards = meld.cards
                    cards.sort(key=lambda x: int(x.rank))
                    suit = cards[0].suit
                    start_rank = cards[0].rank
                    meld_straights.append((suit, start_rank))
            
            # 检查是否有重复的顺子
    
            straight_counts = Counter(meld_straights)
            if any(count >= 2 for count in straight_counts.values()):
                return True
        
        return False
    
    def _is_xi_xiang_feng(self, player) -> bool:
        """判断是否是喜相逢"""
        # 喜相逢：胡牌时有2副花色不同、序数相同的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有顺子的花色和起始点数
        straight_patterns = []
        
        # 检查手牌中的顺子

        hand_counts = Counter(player.hand)
        
        # 检查手牌中是否有顺子
        for card in hand_counts:
            if card.suit in ['万', '筒', '条']:
                rank = int(card.rank)
                next_rank = str(rank + 1)
                next_next_rank = str(rank + 2)
                
                if hand_counts.get(Card(card.suit, next_rank), 0) >= 1 and \
                   hand_counts.get(Card(card.suit, next_next_rank), 0) >= 1:
                    straight_patterns.append((card.suit, rank))
        
        # 检查吃碰杠中的顺子
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type == '吃':
                    cards = meld.cards
                    cards.sort(key=lambda x: int(x.rank))
                    suit = cards[0].suit
                    rank = int(cards[0].rank)
                    straight_patterns.append((suit, rank))
        
        # 检查是否有花色不同但点数相同的顺子
        from collections import defaultdict
        rank_to_suits = defaultdict(set)
        for suit, rank in straight_patterns:
            rank_to_suits[rank].add(suit)
        
        # 只要有一个点数有两种或以上不同花色的顺子，就满足喜相逢
        for suits in rank_to_suits.values():
            if len(suits) >= 2:
                return True
        
        return False
    
    def _is_san_se_san_jie_gao(self, player) -> bool:
        """判断是否是三色三节高"""
        # 三色三节高：胡牌时有3种花色3副依次递增一位数的刻子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否包含三种花色
        suits = set(card.suit for card in player.hand)
        if not {'万', '筒', '条'}.issubset(suits):
            return False
        
        # 收集所有刻子（包括手牌和吃碰杠）
        triplets = []
        
        # 检查手牌中的刻子

        hand_counts = Counter(player.hand)
        for card, count in hand_counts.items():
            if count >= 3:
                triplets.append((card.suit, int(card.rank)))
        
        # 检查吃碰杠中的刻子
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                    # 取刻子/杠中的第一张牌的花色和点数
                    card = meld.cards[0]
                    triplets.append((card.suit, int(card.rank)))
        
        # 检查是否有三种不同花色的刻子，且点数依次递增一位
        if len(triplets) < 3:
            return False
        
        # 按点数排序
        triplets.sort(key=lambda x: x[1])
        
        # 检查是否存在三个连续的刻子，且花色各不相同
        for i in range(len(triplets) - 2):
            t1, t2, t3 = triplets[i], triplets[i+1], triplets[i+2]
            # 检查点数是否依次递增一位
            if t1[1] + 1 == t2[1] and t2[1] + 1 == t3[1]:
                # 检查花色是否各不相同
                suits = {t1[0], t2[0], t3[0]}
                if len(suits) == 3:
                    return True
        
        return False
    
    def _is_san_se_san_tong_shun(self, player) -> bool:
        """判断是否是三色三同顺"""
        # 三色三同顺：胡牌时有3种花色3副序数相同的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否包含三种花色
        suits = set(card.suit for card in player.hand)
        if not {'万', '筒', '条'}.issubset(suits):
            return False
        
        # 统计每种牌的数量
        from collections import defaultdict
        rank_counts = defaultdict(int)
        
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                rank_counts[card.rank] += 1
        
        # 检查是否有三个花色的相同序数的顺子
        for rank, count in rank_counts.items():
            if count >= 3:
                # 检查是否有三种花色的这个序数
                suit_with_rank = set()
                for card in player.hand:
                    if card.suit in ['万', '筒', '条'] and card.rank == rank:
                        suit_with_rank.add(card.suit)
                
                if len(suit_with_rank) == 3:
                    return True
        
        return False
    
    def _is_jin_gou_diao(self, player) -> bool:
        """判断是否是金钩钓"""
        # 金钩钓：牌被吃碰杠放倒后只剩1张牌单钓将胡牌
        return len(player.hand) == 1 and len(player.melds) == 4
    
    def _is_dai_yao_jiu(self, player) -> bool:
        """判断是否是带幺九"""
        # 带幺九：胡牌时每副牌、将牌都有一、九序数牌或字牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查所有牌是否都包含幺九或字牌
        for card in player.hand:
            # 如果是序数牌，检查是否是1或9
            if card.suit in ['万', '筒', '条']:
                if card.rank not in ['1', '9']:
                    return False
            # 如果是字牌，符合要求
        
        return True
    
    def _is_duan_yao_jiu(self, player) -> bool:
        """判断是否是断幺九"""
        # 断幺九：胡牌中无1、9序数牌及字牌
        return all(c.suit in ['万', '筒', '条'] and 2 <= int(c.rank) <= 8 for c in player.hand)
    
    def _is_lian_liu(self, player) -> bool:
        """判断是否是连六"""
        # 连六：胡牌时有6张同一花色序数相连的牌组成2副顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 按花色分组
        from collections import defaultdict
        suit_cards = defaultdict(list)
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_cards[card.suit].append(int(card.rank))
        
        # 检查每种花色中是否有6张连续的牌
        for suit, ranks in suit_cards.items():
            if len(ranks) < 6:
                continue
            
            # 去重并排序
            unique_ranks = sorted(list(set(ranks)))
            
            # 检查是否有6个连续的数字
            for i in range(len(unique_ranks) - 5):
                if unique_ranks[i+5] - unique_ranks[i] == 5:
                    return True
        
        return False
    
    def _is_lao_shao_fu(self, player) -> bool:
        """判断是否是老少副"""
        # 老少副：一种花色的123、789两副顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 按花色分组
        from collections import defaultdict
        suit_cards = defaultdict(list)
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_cards[card.suit].append(int(card.rank))
        
        # 检查每种花色中是否同时有123和789的顺子
        for suit, ranks in suit_cards.items():
            has_123 = all(r in ranks for r in [1, 2, 3])
            has_789 = all(r in ranks for r in [7, 8, 9])
            
            if has_123 and has_789:
                return True
        
        return False
    
    def _is_jian_ke(self, player) -> bool:
        """判断是否是箭刻"""
        # 箭刻：手中有一副中、发、白的箭刻
        return self._count_arrow_ke(player) >= 1
    
    def _is_chang_feng_ke(self, player) -> bool:
        """判断是否是场风刻"""
        # 场风刻：手中有一副东风的场风刻子
        return self._has_ke(player, Card('风', '东'))
    
    def _is_men_feng_ke(self, player) -> bool:
        """判断是否是门风刻"""
        # 门风刻：手中有一副与本门风相同的风刻
        # 需要玩家位置信息支持
        return False
    
    def _is_an_gang(self, player) -> bool:
        """判断是否是暗杠"""
        # 暗杠：自己摸到4张相同的牌开杠
        return len([m for m in player.melds if m.type == '暗杠']) >= 1
    
    def _is_si_gui_yi(self, player) -> bool:
        """判断是否是四归一"""
        # 四归一：包含4张相同的牌胡牌（不能杠出）

        card_counts = Counter(player.hand)
        
        # 检查手牌中是否有4张相同的牌
        for card, count in card_counts.items():
            if count >= 4:
                return True
        
        # 检查手牌+杠牌是否有4张相同的牌（杠牌必须是暗杠）
        for card, count in card_counts.items():
            if count >= 1:
                gang_count = 0
                for meld in player.melds:
                    if meld.type == '暗杠' and meld.cards[0] == card:
                        gang_count += 1
                if count + 4 * gang_count >= 4:
                    return True
        
        return False
    
    def _is_men_qing(self, player) -> bool:
        """判断是否是门清"""
        # 门清：胡牌时无吃碰和明杠
        return not player.melds
    
    def _is_shuang_an_ke(self, player) -> bool:
        """判断是否是双暗刻"""
        # 双暗刻：胡牌时有2个暗刻
        return len([m for m in player.melds if m.type in ['暗刻', '暗杠']]) >= 2
    
    def _is_shuang_tong_ke(self, player) -> bool:
        """判断是否是双同刻"""
        # 双同刻：胡牌时有2副序数相同的刻子
        from collections import defaultdict
        ke_ranks = defaultdict(list)
        
        # 检查手牌中的刻子

        card_counts = Counter(player.hand)
        for card, count in card_counts.items():
            if card.suit in ['万', '筒', '条'] and count >= 3:
                ke_ranks[card.rank].append(card.suit)
        
        # 检查刻子和杠
        for meld in player.melds:
            if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                card = meld.cards[0]
                if card.suit in ['万', '筒', '条']:
                    ke_ranks[card.rank].append(card.suit)
        
        # 检查是否有相同点数的不同花色的刻子
        for rank, suits in ke_ranks.items():
            if len(set(suits)) >= 2:
                return True
        
        return False
    
    def _is_si_hua(self, player) -> bool:
        """判断是否是四花"""
        # 四花：胡牌时补花数量≥4张
        return hasattr(player, 'hua_cards') and len(player.hua_cards) >= 4
    
    def _is_ming_gang(self, player) -> bool:
        """判断是否是明杠"""
        # 明杠：自己有暗刻，碰别人打出的相同牌开杠；或抓进与碰的明刻相同的牌开杠
        return len([m for m in player.melds if m.type == '明杠']) >= 1
    
    def _is_zi_mo(self, player, winning_card) -> bool:
        """判断是否是自摸"""
        # 自摸：自己抓进牌成胡牌
        return winning_card == player.drawn_card
    
    def _is_gang_shang_kai_hua(self, player, winning_card) -> bool:
        """判断是否是杠上开花"""
        # 杠上开花：杠牌/补花后摸牌胡牌
        return hasattr(player, 'last_action') and player.last_action in ['杠牌', '补花'] and winning_card == player.drawn_card
    
    def _is_miao_shou_hui_chun(self, player, winning_card) -> bool:
        """判断是否是妙手回春"""
        # 妙手回春：自摸牌墙最后一张牌胡牌（不计自摸）
        return hasattr(player, 'is_last_card') and player.is_last_card and winning_card == player.drawn_card
    
    def _is_hai_di_lao_yue(self, player, winning_card) -> bool:
        """判断是否是海底捞月"""
        # 海底捞月：胡打出的最后一张牌
        return hasattr(player, 'is_last_card') and player.is_last_card and winning_card != player.drawn_card
    
    def _is_qiang_gang_hu(self, player, winning_card) -> bool:
        """判断是否是抢杠胡"""
        # 抢杠胡：胡别人补杠的那张牌
        return hasattr(player, 'last_action') and player.last_action == '补杠' and winning_card != player.drawn_card
    
    def _is_gang_shang_pao(self, player, winning_card) -> bool:
        """判断是否是杠上炮"""
        # 杠上炮：胡别人杠牌后打出的那张牌
        return hasattr(player, 'last_action') and player.last_action == '杠牌' and winning_card != player.drawn_card
    
    # 辅助方法
    def _count_wind_ke(self, player) -> int:
        """计算风刻数量"""
        wind_kes = 0
        for wind in ['东', '南', '西', '北']:
            if self._has_ke(player, Card('风', wind)):
                wind_kes += 1
        return wind_kes
    
    def _is_shunzi(self, cards) -> bool:
        """判断是否是顺子"""
        if len(cards) != 3:
            return False
        
        # 按点数排序（转换为整数）
        cards.sort(key=lambda x: int(x.rank))
        
        # 检查是否是连续的点数
        return (int(cards[0].rank) + 1 == int(cards[1].rank) and
                int(cards[1].rank) + 1 == int(cards[2].rank))
    
    def _is_kezi(self, cards) -> bool:
        """判断是否是刻子"""
        if len(cards) != 3:
            return False
        return cards[0] == cards[1] == cards[2]
    
    def _is_gangzi(self, cards) -> bool:
        """判断是否是杠子"""
        if len(cards) != 4:
            return False
        return cards[0] == cards[1] == cards[2] == cards[3]
    
    def _count_arrow_ke(self, player) -> int:
        """计算箭刻数量"""
        arrow_kes = 0
        for arrow in ['中', '发', '白']:
            if self._has_ke(player, Card('箭', arrow)):
                arrow_kes += 1
        return arrow_kes
    
    def _has_wind_pair(self, player) -> bool:
        """判断是否有风牌对子"""
        wind_counts = {}
        for card in player.hand:
            if card.suit == '风':
                wind_counts[card.rank] = wind_counts.get(card.rank, 0) + 1
        return any(count >= 2 for count in wind_counts.values())
    
    def _has_arrow_pair(self, player) -> bool:
        """判断是否有箭牌对子"""
        arrow_counts = {}
        for card in player.hand:
            if card.suit == '箭':
                arrow_counts[card.rank] = arrow_counts.get(card.rank, 0) + 1
        return any(count >= 2 for count in arrow_counts.values())
    
    def _has_ke(self, player, card) -> bool:
        """判断是否有特定牌的刻子或杠"""
        # 检查手牌中是否有刻子
        count = sum(1 for c in player.hand if c == card)
        if count >= 3:
            return True
        
        # 检查明刻、明杠、暗杠
        for meld in player.melds:
            if meld.type in ['明刻', '明杠', '暗刻', '暗杠'] and any(c == card for c in meld.cards):
                return True
        
        return False
    
    def _is_seven_pairs(self, player) -> bool:
        """判断是否是七对子"""
        # 七对子：由7个对子组成的胡牌
        hand = player.hand.copy()
        if len(hand) != 14:
            return False
        
        # 检查是否有七个不同的对子
        pairs = set()
        for card in hand:
            if card in pairs:
                pairs.remove(card)
            else:
                pairs.add(card)
        
        return len(pairs) == 0
    
    def _is_pure_suit(self, player) -> bool:
        """判断是否是清一色"""
        # 清一色：只由一种花色序数牌组成的胡牌
        if not player.hand:
            return False
        
        suit = player.hand[0].suit
        if suit not in ['万', '筒', '条']:
            return False
        
        return all(card.suit == suit for card in player.hand)
    
    def _is_mixed_suit(self, player) -> bool:
        """判断是否是混一色"""
        # 混一色：由一种花色序数牌+字牌组成的胡牌
        hand = player.hand
        if not hand:
            return False
        
        suits = {card.suit for card in hand}
        ordinal_suits = suits.intersection(['万', '筒', '条'])
        special_suits = suits.intersection(['风', '箭'])
        
        return len(ordinal_suits) == 1 and special_suits.issubset(['风', '箭'])
    
    def _is_dragon(self, player) -> bool:
        """判断是否是一条龙"""
        # 一条龙：某一花色的1-9牌都有
        hand = player.hand
        
        # 检查每种花色是否有1-9
        for suit in ['万', '筒', '条']:
            ranks = {card.rank for card in hand if card.suit == suit}
            if set(map(str, range(1, 10))).issubset(ranks):
                return True
        
        return False
    
    def _is_all_pairs(self, player) -> bool:
        """判断是否是碰碰胡"""
        # 碰碰胡：由4副刻子（或杠）、将牌组成的胡牌
        if len(player.hand) != 14:
            return False
        
        # 检查是否有4副刻子/杠和1对将牌

        card_counts = Counter(player.hand)
        
        # 统计刻子/杠的数量（包括手牌中的）
        ke_count = 0
        pair_count = 0
        
        for count in card_counts.values():
            if count == 3:
                ke_count += 1
            elif count == 4:
                ke_count += 1  # 杠也算一副刻子
            elif count == 2:
                pair_count += 1
            else:
                return False  # 存在单张牌，不是碰碰胡
        
        # 刻子数量必须为4，对子数量必须为1
        return ke_count == 4 and pair_count == 1
    
    # 辅助方法保留一个版本
    
