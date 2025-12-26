import pytest
from src.core.data.card import Card
from src.core.data.player import Player
from src.rules.tencent_common.score_rules import TencentScoreRules
from src.rules.tencent_common.rule import TencentCommonRule

@pytest.fixture
def player():
    """创建一个玩家实例"""
    player = Player(1, "测试玩家")
    player.hand = []
    player.melds = []
    return player

@pytest.fixture
def rule():
    """创建规则实例"""
    return TencentCommonRule()

@pytest.fixture
def score_rules(rule):
    """创建评分规则实例"""
    return TencentScoreRules(rule)

def test_is_yi_se_si_bu_gao(player, score_rules):
    """测试一色四步高"""
    # 万子一色四步高：123, 234, 345, 456 + 77
    hand = [
        Card("万", "1"), Card("万", "2"), Card("万", "3"),
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "3"), Card("万", "4"), Card("万", "5"),
        Card("万", "4"), Card("万", "5"), Card("万", "6"),
        Card("万", "7"), Card("万", "7")
    ]
    player.hand = hand
    assert score_rules._is_yi_se_si_bu_gao(player) == True

def test_is_tui_bu_dao(player, score_rules):
    """测试推不倒"""
    # 推不倒牌型：筒子2,4,5,6,8,9；条子1,2,3,4,5,8,9；箭牌中
    hand = [
        Card("筒", "2"), Card("筒", "4"), Card("筒", "5"),
        Card("筒", "6"), Card("筒", "8"), Card("筒", "9"),
        Card("条", "1"), Card("条", "2"), Card("条", "3"),
        Card("条", "4"), Card("条", "5"), Card("条", "8"),
        Card("条", "9"), Card("箭", "中")
    ]
    player.hand = hand
    assert score_rules._is_tui_bu_dao(player) == True

def test_is_all_pairs(player, score_rules):
    """测试碰碰胡"""
    # 碰碰胡：4副刻子+1对将牌
    hand = [
        Card("万", "1"), Card("万", "1"), Card("万", "1"),
        Card("万", "2"), Card("万", "2"), Card("万", "2"),
        Card("万", "3"), Card("万", "3"), Card("万", "3"),
        Card("万", "4"), Card("万", "4"), Card("万", "4"),
        Card("万", "5"), Card("万", "5")
    ]
    player.hand = hand
    assert score_rules._is_all_pairs(player) == True

def test_is_si_gui_yi(player, score_rules):
    """测试四归一"""
    # 四归一：手牌中包含4张相同的牌
    hand = [
        Card("万", "1"), Card("万", "1"), Card("万", "1"), Card("万", "1"),
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "5"), Card("万", "6"), Card("万", "7"),
        Card("万", "8"), Card("万", "9"), Card("条", "1"), Card("条", "1")
    ]
    player.hand = hand
    assert score_rules._is_si_gui_yi(player) == True

def test_is_shuang_tong_ke(player, score_rules):
    """测试双同刻"""
    # 双同刻：2副序数相同的刻子
    hand = [
        Card("万", "1"), Card("万", "1"), Card("万", "1"),
        Card("筒", "1"), Card("筒", "1"), Card("筒", "1"),
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "5"), Card("万", "6"), Card("万", "7"),
        Card("万", "8"), Card("万", "9")
    ]
    player.hand = hand
    assert score_rules._is_shuang_tong_ke(player) == True

def test_is_si_hua(player, score_rules):
    """测试四花"""
    # 四花：补花数量≥4张
    player.hua_cards = [
        Card("花", "梅"), Card("花", "兰"), Card("花", "竹"), Card("花", "菊")
    ]
    assert score_rules._is_si_hua(player) == True

def test_is_ming_gang(player, score_rules):
    """测试明杠"""
    # 明杠：玩家有1个明杠
    class Meld:
        def __init__(self, type, cards):
            self.type = type
            self.cards = cards
    player.melds = [Meld("明杠", [Card("万", "1"), Card("万", "1"), Card("万", "1"), Card("万", "1")])]
    assert score_rules._is_ming_gang(player) == True

def test_is_gang_shang_kai_hua(player, score_rules):
    """测试杠上开花"""
    # 杠上开花：最后动作是杠牌，且自摸
    player.last_action = "杠牌"
    player.drawn_card = Card("万", "1")
    assert score_rules._is_gang_shang_kai_hua(player, Card("万", "1")) == True

def test_is_chang_feng_ke(player, score_rules):
    """测试场风刻"""
    # 设置场风为东
    player.chang_feng = '东'
    # 手牌中有东风刻子
    player.hand = [
        Card("风", "东"), Card("风", "东"), Card("风", "东"),
        Card("万", "1"), Card("万", "2"), Card("万", "3"),
        Card("万", "4"), Card("万", "5"), Card("万", "6"),
        Card("万", "7"), Card("万", "8"), Card("万", "9"),
        Card("条", "1"), Card("条", "1")
    ]
    assert score_rules._is_chang_feng_ke(player) == True
    
    # 设置场风为南，但手牌中是东风刻子
    player.chang_feng = '南'
    assert score_rules._is_chang_feng_ke(player) == False

def test_is_men_feng_ke(player, score_rules):
    """测试门风刻"""
    # 设置门风为南
    player.men_feng = '南'
    # 手牌中有南风刻子
    player.hand = [
        Card("风", "南"), Card("风", "南"), Card("风", "南"),
        Card("万", "1"), Card("万", "2"), Card("万", "3"),
        Card("万", "4"), Card("万", "5"), Card("万", "6"),
        Card("万", "7"), Card("万", "8"), Card("万", "9"),
        Card("条", "1"), Card("条", "1")
    ]
    assert score_rules._is_men_feng_ke(player) == True
    
    # 设置门风为东，但手牌中是南风刻子
    player.men_feng = '东'
    assert score_rules._is_men_feng_ke(player) == False

def test_is_yao_jiu_ke(player, score_rules):
    """测试幺九刻"""
    # 手牌中有万1的刻子
    player.hand = [
        Card("万", "1"), Card("万", "1"), Card("万", "1"),
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "5"), Card("万", "6"), Card("万", "7"),
        Card("万", "8"), Card("万", "9"),
        Card("条", "2"), Card("条", "3"), Card("条", "4")
    ]
    assert score_rules._is_yao_jiu_ke(player) == True
    
    # 手牌中有筒9的刻子
    player.hand = [
        Card("筒", "9"), Card("筒", "9"), Card("筒", "9"),
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "5"), Card("万", "6"), Card("万", "7"),
        Card("万", "8"), Card("万", "9"),
        Card("条", "2"), Card("条", "3"), Card("条", "4")
    ]
    assert score_rules._is_yao_jiu_ke(player) == True
    
    # 手牌中没有幺九刻
    player.hand = [
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "5"), Card("万", "6"), Card("万", "7"),
        Card("万", "8"), Card("万", "9"),
        Card("条", "2"), Card("条", "3"), Card("条", "4"),
        Card("筒", "5"), Card("筒", "6"), Card("筒", "7")
    ]
    assert score_rules._is_yao_jiu_ke(player) == False

def test_calculate_fans_1_fans(player, score_rules):
    """测试1番番型的计算"""
    # 测试自摸
    player.drawn_card = Card("万", "5")
    assert score_rules._check_1_fans(player, Card("万", "5")) == 1
    
    # 测试幺九刻
    player.hand = [
        Card("万", "1"), Card("万", "1"), Card("万", "1"),  # 幺九刻
        Card("万", "2"), Card("万", "3"), Card("万", "4"),
        Card("万", "5"), Card("万", "6"), Card("万", "7"),
        Card("万", "8"), Card("万", "9"), Card("条", "1"),
        Card("条", "2"), Card("条", "3")
    ]
    assert score_rules._check_1_fans(player, Card("万", "5")) == 2  # 自摸+幺九刻

def test_calculate_score(player, score_rules):
    """测试分数计算"""
    # 基本情况：自摸（1番），底分10，但规则中max_fans=10，所以最终番数为10
    player.drawn_card = Card("万", "5")
    player.hand = [
        Card("万", "1"), Card("万", "2"), Card("万", "3"),
        Card("万", "4"), Card("万", "5"), Card("万", "6"),
        Card("万", "7"), Card("万", "8"), Card("万", "9"),
        Card("条", "1"), Card("条", "2"), Card("条", "3"),
        Card("筒", "4"), Card("筒", "4")
    ]
    # 调试：打印实际计算的番数
    fans = score_rules._calculate_fans(player, Card("万", "5"))
    print(f"实际番数: {fans}")
    assert score_rules.calculate_score(player, Card("万", "5")) == 10 * 1 * 10  # 10番 × 1倍 × 底分10  

    # 庄家翻倍：自摸（10番），庄家（×2倍）
    player.is_dealer = True
    assert score_rules.calculate_score(player, Card("万", "5")) == 10 * 2 * 10  # 10番 × 2倍 × 底分10  

    # 创建新玩家实例测试杠上开花
    new_player = Player(2, "测试玩家2")
    new_player.drawn_card = Card("万", "5")
    new_player.hand = [
        Card("万", "1"), Card("万", "2"), Card("万", "3"),
        Card("万", "4"), Card("万", "5"), Card("万", "6"),
        Card("万", "7"), Card("万", "8"), Card("万", "9"),
        Card("条", "1"), Card("条", "2"), Card("条", "3"),
        Card("筒", "4"), Card("筒", "4")
    ]
    new_player.melds = []
    new_player.last_action = "杠牌"
    # 杠上开花：自摸+杠上开花（×2倍）
    assert score_rules.calculate_score(new_player, Card("万", "5")) == 10 * 2 * 10  # 10番 × 2倍 × 底分10  

    # 连杠收益：连杠2次（×3倍）
    new_player.last_action = None
    new_player.consecutive_gang_count = 2
    assert score_rules.calculate_score(new_player, Card("万", "5")) == 10 * 3 * 10  # 10番 × 3倍 × 底分10  

    # 组合情况：自摸+箭刻（4番），庄家（×2倍），杠上开花（×2倍）
    new_player.drawn_card = Card("箭", "中")
    player.is_dealer = True
    player.last_action = "杠牌"
    player.consecutive_gang_count = 0
    player.hand = [
        Card("箭", "中"), Card("箭", "中"), Card("箭", "中"),
        Card("万", "1"), Card("万", "2"), Card("万", "3"),
        Card("万", "4"), Card("万", "5"), Card("万", "6"),
        Card("万", "7"), Card("万", "8"), Card("万", "9"),
        Card("条", "1"), Card("条", "1")
    ]
    assert score_rules.calculate_score(player, Card("箭", "中")) == 5 * 2 * 2 * 10  # 5番（箭刻4番+自摸1番） × 2倍（庄家） × 2倍（杠上开花） × 底分10
