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
        # 底分
        base_score = 10  # 默认底分，可根据游戏设置调整
        
        # 计算番数总和
        fans_total = self._calculate_fans(player, winning_card)
        
        # 计算翻倍（杠上开花、杠上炮、抢杠胡等属于翻倍番型）
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
        
        # 庄家翻倍
        if hasattr(player, 'is_dealer') and player.is_dealer:
            multiplier *= 2
        
        # 根据连杠次数调整倍数
        if hasattr(player, 'consecutive_gang_count') and player.consecutive_gang_count > 0:
            # 连杠次数越多，倍数越高
            multiplier *= (player.consecutive_gang_count + 1)
        
        # 计算最终分数：番数总和 × 翻倍 × 底分
        final_score = fans_total * multiplier * base_score
        
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
            fans += 64
        
        # 小三元
        if self._is_xiao_san_yuan(player):
            fans += 64
        
        # 字一色
        if self._is_zi_yi_se(player):
            fans += 64
        
        # 四暗刻
        if self._is_si_an_ke(player):
            fans += 64
        
        # 一色双龙会
        if self._is_yi_se_shuang_long_hui(player):
            fans += 64
        
        # 清幺九
        if self._is_qing_yao_jiu(player):
            fans += 64
        
        # 人胡
        if self._is_ren_hu(player):
            fans += 64
        
        return fans
    
    def _check_48_fans(self, player) -> int:
        """检查48番番型"""
        fans = 0
        
        # 四同顺
        if self._is_si_tong_shun(player):
            fans += 48
        
        # 四连刻
        if self._is_si_lian_ke(player):
            fans += 48
        
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
        
        # 三色三节高
        if self._is_san_se_san_jie_gao(player):
            fans += 12
        
        # 全带五
        if self._is_quan_dai_wu(player):
            fans += 12
        
        # 双暗刻
        if self._is_shuang_an_ke(player):
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
        
        # 双暗杠
        if self._is_shuang_an_gang(player):
            fans += 8
        
        # 明杠
        if self._is_ming_gang(player):
            fans += 8
        
        # 不求人
        if self._is_bu_qiu_ren(player):
            fans += 8
        
        # 双箭刻
        if self._is_shuang_jian_ke(player):
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
        
        # 幺九刻
        if self._is_yao_jiu_ke(player):
            fans += 1
        
        return fans
    
    def _check_double_fans(self, player, winning_card, total_fans) -> int:
        """检查翻倍番型（已在calculate_score中直接处理翻倍逻辑）"""
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
        
        # 检查手牌是否包含所有必要的牌（允许有一个对子）
        hand_set = set(player.hand)
        missing_cards = required_cards - hand_set
        
        # 如果缺少的牌数超过1，或者缺少的牌数为1但没有该牌的对子，则不符合条件
        if len(missing_cards) > 1:
            return False
        
        if len(missing_cards) == 1:
            # 检查是否有该牌的对子
            missing_card = missing_cards.pop()
            if player.hand.count(missing_card) != 2:
                return False
        else:
            # 检查是否有任意一个字牌的对子
            pair_found = False
            for card in required_cards:
                if player.hand.count(card) == 2:
                    pair_found = True
                    break
            if not pair_found:
                return False
        
        return True
    
    def _is_tian_hu(self, player, winning_card) -> bool:
        """判断是否是天胡"""
        # 天胡：庄家在发完牌后直接胡牌
        # 需要游戏状态支持
        return False
    
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
        card_counts = Counter(player.hand)
        suit = next(iter(suits))
        
        # 检查是否符合1112345678999的牌型
        expected_counts = {
            Card(suit, '1'): 3,
            Card(suit, '2'): 1,
            Card(suit, '3'): 1,
            Card(suit, '4'): 1,
            Card(suit, '5'): 1,
            Card(suit, '6'): 1,
            Card(suit, '7'): 1,
            Card(suit, '8'): 1,
            Card(suit, '9'): 3
        }
        
        return card_counts == expected_counts
    
    def _is_shi_ba_luo_han(self, player) -> bool:
        """判断是否是十八罗汉"""
        # 十八罗汉：胡牌时手中有4副杠牌
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type in ['明杠', '暗杠']]) == 4
    
    def _is_lian_qi_dui(self, player) -> bool:
        """判断是否是连七对"""
        # 连七对：由同一花色序数牌组成的序数相连的7个对子
        if not self._is_seven_pairs(player):
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        # 提取所有牌的点数并去重
        ranks = sorted(list(set(int(card.rank) for card in player.hand)))
        
        # 检查点数是否连续
        for i in range(1, len(ranks)):
            if ranks[i] - ranks[i-1] != 1:
                return False
        
        return True
    
    def _is_lv_yi_se(self, player) -> bool:
        """判断是否是绿一色"""
        # 绿一色：由2、3、4、6、8条及发财组成的胡牌
        green_cards = {
            Card('条', '2'),
            Card('条', '3'),
            Card('条', '4'),
            Card('条', '6'),
            Card('条', '8'),
            Card('箭', '发')
        }
        
        return all(card in green_cards for card in player.hand)
    
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
        return all(card.suit in ['风', '箭'] for card in player.hand)
    
    def _is_si_an_ke(self, player) -> bool:
        """判断是否是四暗刻"""
        # 四暗刻：4个暗刻（暗杠）组成的胡牌
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type in ['暗刻', '暗杠']]) == 4
    
    def _is_yi_se_shuang_long_hui(self, player) -> bool:
        """判断是否是一色双龙会"""
        # 一色双龙会：一种花色的两个老少副，5为将牌
        if len(player.hand) != 14:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        suit = next(iter(suits))
        
        # 统计每种牌的数量
        card_counts = Counter(player.hand)
        
        # 检查是否有两个老少副（123和789）
        has_low_straight = card_counts.get(Card(suit, '1'), 0) >= 1 and \
                          card_counts.get(Card(suit, '2'), 0) >= 1 and \
                          card_counts.get(Card(suit, '3'), 0) >= 1
        
        has_high_straight = card_counts.get(Card(suit, '7'), 0) >= 1 and \
                           card_counts.get(Card(suit, '8'), 0) >= 1 and \
                           card_counts.get(Card(suit, '9'), 0) >= 1
        
        # 检查是否有5的对子
        has_five_pair = card_counts.get(Card(suit, '5'), 0) == 2
        
        return has_low_straight and has_high_straight and has_five_pair
    
    def _is_qing_yao_jiu(self, player) -> bool:
        """判断是否是清幺九"""
        # 清幺九：只由序数牌一、九组成的胡牌
        return all(card.suit in ['万', '筒', '条'] and card.rank in ['1', '9'] for card in player.hand)
    
    def _is_ren_hu(self, player) -> bool:
        """判断是否是人胡"""
        # 人胡：非庄家发完牌后第一轮就吃胡
        # 需要游戏状态支持
        return False
    
    def _is_si_tong_shun(self, player) -> bool:
        """判断是否是四同顺"""
        # 四同顺：一种花色4副序数相同的顺子
        # 实现复杂，暂不实现
        return False
    
    def _is_si_lian_ke(self, player) -> bool:
        """判断是否是四连刻"""
        # 四连刻：一种花色4副依次递增一位数的刻子
        # 实现复杂，暂不实现
        return False
    
    def _is_yi_se_si_bu_gao(self, player) -> bool:
        """判断是否是一色四步高"""
        # 一色四步高：一种花色4副依次递增一位数或二位数的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否是万子一色四步高：123, 234, 345, 456 + 对子
        # 统计万子各点数的数量
        count = Counter(player.hand)
        expected_counts = {
            Card('万', '1'): 1,
            Card('万', '2'): 2,
            Card('万', '3'): 3,
            Card('万', '4'): 3,
            Card('万', '5'): 2,
            Card('万', '6'): 1,
            Card('万', '7'): 2
        }
        
        return count == expected_counts
    
    def _is_shi_er_jin_chai(self, player) -> bool:
        """判断是否是十二金钗"""
        # 十二金钗：胡牌时手中有3副杠牌
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type in ['明杠', '暗杠']]) == 3
    
    def _is_hun_yao_jiu(self, player) -> bool:
        """判断是否是混幺九"""
        # 混幺九：由序数牌一、九和字牌组成的胡牌
        return all(card.suit in ['风', '箭'] or (card.suit in ['万', '筒', '条'] and card.rank in ['1', '9']) for card in player.hand)
    
    def _is_seven_pairs(self, player) -> bool:
        """判断是否是七对"""
        # 七对：由7个对子组成的胡牌
        if len(player.hand) != 14:
            return False
        
        # 统计每种牌的数量
        card_counts = Counter(player.hand)
        return all(count == 2 for count in card_counts.values()) and len(card_counts) == 7
    
    def _is_pure_suit(self, player) -> bool:
        """判断是否是清一色"""
        # 清一色：只由一种花色序数牌组成的胡牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        return len(suits) == 1 and next(iter(suits)) in ['万', '筒', '条']
    
    def _is_quan_shuang_ke(self, player) -> bool:
        """判断是否是全双刻"""
        # 全双刻：胡牌时手牌都是双数的序数牌
        return all(card.suit in ['万', '筒', '条'] and int(card.rank) % 2 == 0 for card in player.hand)
    
    def _is_quan_da(self, player) -> bool:
        """判断是否是全大"""
        # 全大：胡牌时手牌都是七、八、九的序数牌
        return all(card.suit in ['万', '筒', '条'] and int(card.rank) >= 7 for card in player.hand)
    
    def _is_quan_zhong(self, player) -> bool:
        """判断是否是全中"""
        # 全中：胡牌时手牌都是四、五、六的序数牌
        return all(card.suit in ['万', '筒', '条'] and 4 <= int(card.rank) <= 6 for card in player.hand)
    
    def _is_quan_xiao(self, player) -> bool:
        """判断是否是全小"""
        # 全小：胡牌时手牌都是一、二、三的序数牌
        return all(card.suit in ['万', '筒', '条'] and int(card.rank) <= 3 for card in player.hand)
    
    def _is_san_lian_ke(self, player) -> bool:
        """判断是否是三连刻"""
        # 三连刻：一种花色3副依次递增一位数字的刻子
        # 实现复杂，暂不实现
        return False
    
    def _is_san_tong_shun(self, player) -> bool:
        """判断是否是三同顺"""
        # 三同顺：一种花色3副序数相同的顺子
        # 实现复杂，暂不实现
        return False
    
    def _is_qing_long(self, player) -> bool:
        """判断是否是清龙"""
        # 清龙：一种花色1-9相连的序数牌（需要形成完整的1-9顺子）
        # 注意：实际规则是需要有3副顺子构成1-9相连，如123,456,789
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否只有一种花色
        suits = set(card.suit for card in player.hand)
        if len(suits) != 1 or next(iter(suits)) not in ['万', '筒', '条']:
            return False
        
        # 收集所有该花色的牌
        suit = next(iter(suits))
        cards = [card for card in player.hand if card.suit == suit]
        
        # 统计每种牌的数量
        from collections import Counter
        rank_counts = Counter(int(card.rank) for card in cards)
        
        # 检查是否包含1-9的所有点数
        if set(range(1, 10)) - set(rank_counts.keys()):
            return False
        
        # 这里需要更复杂的逻辑来检查是否形成完整的1-9顺子
        # 简化实现：当前暂不实现，返回False
        return False
    
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
                second = unique_ranks[j]
                for k in range(j + 1, len(unique_ranks)):
                    third = unique_ranks[k]
                    # 检查是否符合三步高的条件
                    if (second - start in [1, 2] and \
                        third - second in [1, 2]):
                        return True
        
        return False
    
    def _is_san_tong_ke(self, player) -> bool:
        """判断是否是三同刻"""
        # 三同刻：3个序数相同的刻子（杠）
        # 实现复杂，暂不实现
        return False
    
    def _is_san_an_ke(self, player) -> bool:
        """判断是否是三暗刻"""
        # 三暗刻：胡牌时包含3个暗刻
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type in ['暗刻', '暗杠']]) >= 3
    
    def _is_qi_xing_bu_kao(self, player) -> bool:
        """判断是否是七星不靠"""
        # 七星不靠：有7个单张的东南西北中发白，加3种花色按147、258、369组合的牌
        if len(player.hand) != 14:
            return False
        
        # 检查是否有7个单张的东南西北中发白
        required_wind_arrow = {
            Card('风', '东'), Card('风', '南'), Card('风', '西'), Card('风', '北'),
            Card('箭', '中'), Card('箭', '发'), Card('箭', '白')
        }
        
        wind_arrow_cards = set(card for card in player.hand if card in required_wind_arrow)
        if len(wind_arrow_cards) != 7:
            return False
        
        # 检查剩下的牌是否符合147、258、369的组合
        remaining_cards = [card for card in player.hand if card not in required_wind_arrow]
        if len(remaining_cards) != 7:
            return False
        
        # 检查剩下的牌是否符合147、258、369的组合
        for card in remaining_cards:
            if card.suit not in ['万', '筒', '条']:
                return False
            if int(card.rank) % 3 not in [1, 2, 0]:  # 1,4,7 → 1 mod 3; 2,5,8 → 2 mod 3; 3,6,9 → 0 mod 3
                return False
        
        return True
    
    def _is_tui_bu_dao(self, player) -> bool:
        """判断是否是推不倒"""
        # 推不倒：由牌面图形无上下区别的牌组成的胡牌
        # 推不倒牌型：筒子2,4,5,6,8,9；条子1,2,3,4,5,8,9；箭牌中
        tui_bu_dao_cards = {
            # 筒子
            Card('筒', '2'), Card('筒', '4'), Card('筒', '5'), Card('筒', '6'), Card('筒', '8'), Card('筒', '9'),
            # 条子
            Card('条', '1'), Card('条', '2'), Card('条', '3'), Card('条', '4'), Card('条', '5'), Card('条', '8'), Card('条', '9'),
            # 箭牌
            Card('箭', '中')
        }
        
        return all(card in tui_bu_dao_cards for card in player.hand)
    
    def _is_chun_dai_yao_jiu(self, player) -> bool:
        """判断是否是纯带幺九"""
        # 纯带幺九：胡牌时每副牌、将牌都包含一或九的序数牌
        # 实现复杂，暂不实现
        return False
    
    def _is_san_feng_ke(self, player) -> bool:
        """判断是否是三风刻"""
        # 三风刻：胡牌时包含3副风刻
        return self._count_wind_ke(player) == 3
    
    def _is_quan_dan(self, player) -> bool:
        """判断是否是全单"""
        # 全单：胡牌时手牌都是单数的序数牌
        return all(card.suit in ['万', '筒', '条'] and int(card.rank) % 2 == 1 for card in player.hand)
    
    def _is_san_se_shuang_long_hui(self, player) -> bool:
        """判断是否是三色双龙会"""
        # 三色双龙会：2种花色2个老少副，第三种花色5的对子
        # 实现复杂，暂不实现
        return False
    
    def _is_shuang_an_gang(self, player) -> bool:
        """判断是否是双暗杠"""
        # 双暗杠：胡牌时有2个暗杠
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type == '暗杠']) >= 2
    
    def _is_shuang_jian_ke(self, player) -> bool:
        """判断是否是双箭刻"""
        # 双箭刻：胡牌时有2副箭刻
        return self._count_arrow_ke(player) == 2
    
    def _is_wu_men_qi(self, player) -> bool:
        """判断是否是五门齐"""
        # 五门齐：胡牌时3种序数牌、风、箭牌齐全
        suits = set(card.suit for card in player.hand)
        return {'万', '筒', '条', '风', '箭'}.issubset(suits)
    
    def _is_all_pairs(self, player) -> bool:
        """判断是否是碰碰胡"""
        # 碰碰胡：由4副刻子（或杠）、将牌组成的胡牌
        if len(player.hand) != 14:
            return False
        
        # 统计每种牌的数量
        card_counts = Counter(player.hand)
        counts = sorted(card_counts.values())
        
        # 碰碰胡牌型：4个刻子（3张相同）和1个对子（2张相同）
        return counts == [2, 3, 3, 3, 3]
    
    def _is_hua_long(self, player) -> bool:
        """判断是否是花龙"""
        # 花龙：3种花色的3副顺子连接成1-9的序数牌
        # 实现复杂，暂不实现
        return False
    
    def _is_zu_he_long(self, player) -> bool:
        """判断是否是组合龙"""
        # 组合龙：包含3种花色的147、258、369的9张序数牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 检查是否包含3种花色的147、258、369
        suit_groups = defaultdict(set)
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_groups[card.suit].add(int(card.rank))
        
        # 需要有3种花色
        if len(suit_groups) != 3:
            return False
        
        # 检查每种花色是否属于不同的组（147、258、369）
        groups = []
        for ranks in suit_groups.values():
            # 检查该花色属于哪个组
            group = None
            if all(r in ranks for r in [1, 4, 7]):
                group = 1
            elif all(r in ranks for r in [2, 5, 8]):
                group = 2
            elif all(r in ranks for r in [3, 6, 9]):
                group = 3
            if group:
                groups.append(group)
        
        # 检查是否包含所有3个组
        return len(set(groups)) == 3
    
    def _is_quan_bu_kao(self, player) -> bool:
        """判断是否是全不靠"""
        # 全不靠：由单张3种花色的147、258、369序数牌及字牌中任意14张组成
        # 实现复杂，暂不实现
        return False
    
    def _is_san_se_san_tong_shun(self, player) -> bool:
        """判断是否是三色三同顺"""
        # 三色三同顺：胡牌时有3种花色3副序数相同的顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 按花色分组
        suit_cards = defaultdict(list)
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_cards[card.suit].append(int(card.rank))
        
        # 需要有3种花色
        if len(suit_cards) != 3:
            return False
        
        # 检查是否存在3种花色序数相同的顺子
        for i in range(1, 8):
            # 检查i, i+1, i+2的顺子是否在所有花色中都存在
            found = True
            for suit in ['万', '筒', '条']:
                ranks = suit_cards[suit]
                if i not in ranks or (i + 1) not in ranks or (i + 2) not in ranks:
                    found = False
                    break
            if found:
                return True
        
        return False
    
    def _is_san_se_san_jie_gao(self, player) -> bool:
        """判断是否是三色三节高"""
        # 三色三节高：3种花色3副依次递增一位数的刻子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有刻子
        triplets = []
        
        # 检查手牌中的刻子
        card_counts = Counter(player.hand)
        for card, count in card_counts.items():
            if card.suit in ['万', '筒', '条'] and count >= 3:
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
    
    def _is_quan_dai_wu(self, player) -> bool:
        """判断是否是全带五"""
        # 全带五：胡牌时每副牌、将牌都包含5的序数牌
        # 实现复杂，暂不实现
        return False
    
    def _is_shuang_an_ke(self, player) -> bool:
        """判断是否是双暗刻"""
        # 双暗刻：胡牌时有2个暗刻
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type in ['暗刻', '暗杠']]) >= 2
    
    def _is_jin_gou_diao(self, player) -> bool:
        """判断是否是金钩钓"""
        # 金钩钓：牌被吃碰杠放倒后只剩1张牌单钓将胡牌
        return len(player.hand) == 1 and len(player.melds) == 4
    
    def _is_dai_yao_jiu(self, player) -> bool:
        """判断是否是带幺九"""
        # 带幺九：胡牌时每副牌、将牌都有一、九序数牌或字牌
        # 实现复杂，暂不实现
        return False
    
    def _is_mixed_suit(self, player) -> bool:
        """判断是否是混一色"""
        # 混一色：由一种花色序数牌+字牌组成的胡牌
        if len(player.hand) not in [13, 14]:
            return False
        
        # 收集所有花色
        suits = set(card.suit for card in player.hand)
        
        # 必须包含字牌和一种花色
        return len(suits) == 2 and {'风', '箭'}.intersection(suits) and {'万', '筒', '条'}.intersection(suits)
    
    def _is_duan_yao_jiu(self, player) -> bool:
        """判断是否是断幺九"""
        # 断幺九：胡牌中无1、9序数牌及字牌
        return all(card.suit in ['万', '筒', '条'] and 2 <= int(card.rank) <= 8 for card in player.hand)
    
    def _is_yi_ban_gao(self, player) -> bool:
        """判断是否是一般高"""
        # 一般高：由一种花色2副相同的顺子组成
        # 实现复杂，暂不实现
        return False
    
    def _is_xi_xiang_feng(self, player) -> bool:
        """判断是否是喜相逢"""
        # 喜相逢：2种花色2副序数相同的顺子
        # 实现复杂，暂不实现
        return False
    
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
            
            # 检查是否有6张连续的牌
            for i in range(len(unique_ranks) - 5):
                if unique_ranks[i+5] - unique_ranks[i] == 5:
                    return True
        
        return False
    
    def _is_lao_shao_fu(self, player) -> bool:
        """判断是否是老少副"""
        # 老少副：一种花色的123、789两副顺子
        if len(player.hand) not in [13, 14]:
            return False
        
        # 统计每种花色的123和789顺子数量
        suit_has_123 = set()
        suit_has_789 = set()
        
        # 统计手牌中每种花色的点数
        from collections import defaultdict
        suit_ranks = defaultdict(set)
        for card in player.hand:
            if card.suit in ['万', '筒', '条']:
                suit_ranks[card.suit].add(int(card.rank))
        
        # 检查每种花色是否有123顺子
        for suit, ranks in suit_ranks.items():
            if 1 in ranks and 2 in ranks and 3 in ranks:
                suit_has_123.add(suit)
            if 7 in ranks and 8 in ranks and 9 in ranks:
                suit_has_789.add(suit)
        
        # 检查是否有同时包含123和789顺子的花色
        return any(suit in suit_has_789 for suit in suit_has_123)
    
    def _is_jian_ke(self, player) -> bool:
        """判断是否是箭刻"""
        # 箭刻：手中有一副中、发、白的箭刻
        return self._count_arrow_ke(player) >= 1
    
    def _is_chang_feng_ke(self, player) -> bool:
        """判断是否是场风刻"""
        # 场风刻：胡牌时有场风的刻子
        if not hasattr(player, 'chang_feng'):
            return False
        
        return self._has_ke(player, Card('风', player.chang_feng))
    
    def _is_men_feng_ke(self, player) -> bool:
        """判断是否是门风刻"""
        # 门风刻：胡牌时有门风的刻子
        if not hasattr(player, 'men_feng'):
            return False
        
        return self._has_ke(player, Card('风', player.men_feng))
    
    def _is_an_gang(self, player) -> bool:
        """判断是否是暗杠"""
        # 暗杠：自己摸到4张相同的牌开杠
        if not hasattr(player, 'melds'):
            return False
        
        return len([meld for meld in player.melds if meld.type == '暗杠']) >= 1
    
    def _is_si_gui_yi(self, player) -> bool:
        """判断是否是四归一"""
        # 四归一：胡牌时有4张相同的牌（不能杠出）
        card_counts = Counter(player.hand)
        return any(count == 4 for count in card_counts.values())
    
    def _is_men_qing(self, player) -> bool:
        """判断是否是门清"""
        # 门清：胡牌时无吃碰和明杠
        if not hasattr(player, 'melds'):
            return True
        
        return all(meld.type in ['暗杠'] for meld in player.melds)
    
    def _is_shuang_tong_ke(self, player) -> bool:
        """判断是否是双同刻"""
        # 双同刻：胡牌时有2副序数相同的刻子
        # 统计每种点数的刻子数量
        rank_counts = {}  # key: 点数, value: 刻子数量
        
        # 检查手牌中的刻子
        card_counts = Counter(player.hand)
        for card, count in card_counts.items():
            if count >= 3:
                rank = card.rank
                rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        # 检查吃碰杠中的刻子
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type in ['明刻', '暗刻', '明杠', '暗杠']:
                    card = meld.cards[0]
                    rank = card.rank
                    rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        # 检查是否有至少2副序数相同的刻子
        return any(count >= 2 for count in rank_counts.values())
    
    def _is_si_hua(self, player) -> bool:
        """判断是否是四花"""
        # 四花：胡牌时补花数量≥4张
        if hasattr(player, 'huapai_count'):
            return player.huapai_count >= 4
        elif hasattr(player, 'hua_cards'):
            return len(player.hua_cards) >= 4
        
        return False
    
    def _is_ming_gang(self, player) -> bool:
        """判断是否是明杠"""
        # 明杠：自己有暗刻，碰别人打出的相同牌开杠；或抓进与碰的明刻相同的牌开杠
        if not hasattr(player, 'melds'):
            return False
        
        return len([m for m in player.melds if m.type == '明杠']) >= 1
    
    def _is_zi_mo(self, player, winning_card) -> bool:
        """判断是否是自摸"""
        # 自摸：自己抓进牌成胡牌
        return winning_card == player.drawn_card
    
    def _is_gang_shang_kai_hua(self, player, winning_card) -> bool:
        """判断是否是杠上开花"""
        # 杠上开花：杠牌/补花后摸牌胡牌
        return hasattr(player, 'last_action') and player.last_action in ['明杠', '暗杠', '补杠', '补花', '杠牌'] and winning_card == player.drawn_card
    
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
        from src.core.data.game_state import GameState
        if hasattr(player, 'game_state'):
            game_state = player.game_state
            if game_state.last_discarded_card:
                last_player = game_state.last_discarded_card.from_player
                return hasattr(last_player, 'last_action') and last_player.last_action == '补杠' and winning_card == game_state.last_discarded_card.card
        return False
    
    def _is_gang_shang_pao(self, player, winning_card) -> bool:
        """判断是否是杠上炮"""
        # 杠上炮：胡别人杠牌后打出的那张牌
        # 注意：这里的player是胡牌玩家，需要检查的是打出被胡牌的玩家的last_action
        from src.core.data.game_state import GameState
        if hasattr(player, 'game_state'):
            game_state = player.game_state
            if game_state.last_discarded_card:
                last_player = game_state.last_discarded_card.from_player
                return hasattr(last_player, 'last_action') and last_player.last_action in ['明杠', '暗杠', '补杠', '杠牌'] and winning_card == game_state.last_discarded_card.card
        return False
    
    def _is_bu_qiu_ren(self, player) -> bool:
        """判断是否是不求人"""
        # 不求人：门清自摸
        # 实现复杂，暂不实现
        return False
    
    # 辅助方法
    def _count_wind_ke(self, player) -> int:
        """计算风刻数量"""
        wind_kes = 0
        for wind in ['东', '南', '西', '北']:
            if self._has_ke(player, Card('风', wind)):
                wind_kes += 1
        return wind_kes
    
    def _count_arrow_ke(self, player) -> int:
        """计算箭刻数量"""
        arrow_kes = 0
        for arrow in ['中', '发', '白']:
            if self._has_ke(player, Card('箭', arrow)):
                arrow_kes += 1
        return arrow_kes
    
    def _has_ke(self, player, card) -> bool:
        """判断是否有特定牌的刻子或杠"""
        # 检查手牌中是否有刻子
        count = sum(1 for c in player.hand if c == card)
        if count >= 3:
            return True
        
        # 检查明刻、明杠、暗杠
        if hasattr(player, 'melds'):
            for meld in player.melds:
                if meld.type in ['明刻', '明杠', '暗刻', '暗杠'] and any(c == card for c in meld.cards):
                    return True
        
        return False
    
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
    
    def _is_yao_jiu_ke(self, player) -> bool:
        """判断是否是幺九刻"""
        # 幺九刻：手中有一副1或9的序数牌刻子（必须是3张相同的牌）
        # 检查1的刻子
        for suit in ['万', '筒', '条']:
            count = sum(1 for c in player.hand if c == Card(suit, '1'))
            if count >= 3:
                return True
        # 检查9的刻子
        for suit in ['万', '筒', '条']:
            count = sum(1 for c in player.hand if c == Card(suit, '9'))
            if count >= 3:
                return True
        return False
    
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
            
            # 检查是否有6张连续的牌
            for i in range(len(unique_ranks) - 5):
                if unique_ranks[i+5] - unique_ranks[i] == 5:
                    return True
        
        return False