from src.core.data.card import Card
from src.core.data.player import Player
from src.core.data.game_state import GameState
from src.rules.tencent_common.hu_rules import TencentHuRules
from src.rules.tencent_common.score_rules import TencentScoreRules
from src.rules.tencent_common.rule import TencentCommonRule
from src.rules.tencent_common.action_rules import TencentActionRules

# 创建规则实例
rule = TencentCommonRule()

# 创建玩家实例
player = Player(1, "测试玩家")
player.hand = []
player.melds = []

# 创建游戏状态实例
game_state = GameState()
game_state.deck = []
game_state.discard_pile = []
game_state.current_player = player

# 创建规则实例
hu_rules = TencentHuRules(rule)
score_rules = TencentScoreRules(rule)
action_rules = TencentActionRules(rule)

print("测试基础行牌规则和胡牌逻辑...")
print("=" * 50)

# 测试1：补花功能
print("\n1. 测试补花功能：")
player.hand = [Card("花", "梅"), Card("万", "1"), Card("万", "2"), Card("万", "3")]
can_flower = action_rules.can_flower(player)
print(f"   手牌中有花牌时，是否可以补花: {can_flower}")
assert can_flower == True, "补花功能测试失败"

player.hand = [Card("万", "1"), Card("万", "2"), Card("万", "3")]
can_flower = action_rules.can_flower(player)
print(f"   手牌中没有花牌时，是否可以补花: {can_flower}")
assert can_flower == False, "补花功能测试失败"
print("   ✅ 补花功能测试通过")

# 测试2：基础胡牌条件
print("\n2. 测试基础胡牌条件：")
# 简单的四组面子+一对将牌
player.hand = [
    Card("万", "1"), Card("万", "2"), Card("万", "3"),  # 顺子
    Card("万", "4"), Card("万", "5"), Card("万", "6"),  # 顺子
    Card("筒", "1"), Card("筒", "1"), Card("筒", "1"),  # 刻子
    Card("条", "5"), Card("条", "5"), Card("条", "5"),  # 刻子
    Card("风", "东"), Card("风", "东")                     # 将牌
]
player.drawn_card = None
can_hu = hu_rules._check_basic_hu_condition(player, Card("风", "东"))
print(f"   符合四组面子+一对将牌的牌型，是否能胡牌: {can_hu}")
assert can_hu == True, "基础胡牌条件测试失败"
print("   ✅ 基础胡牌条件测试通过")

# 测试3：鸡胡只能自摸
print("\n3. 测试鸡胡只能自摸：")
# 鸡胡牌型（只有自摸番）
player.hand = [
    Card("万", "1"), Card("万", "2"), Card("万", "3"),
    Card("万", "4"), Card("万", "5"), Card("万", "6"),
    Card("万", "7"), Card("万", "8"), Card("万", "9"),
    Card("筒", "1"), Card("筒", "1"), Card("筒", "1"),
    Card("条", "2"), Card("条", "2")
]

# 自摸情况
player.drawn_card = Card("条", "2")
can_hu_self = hu_rules.can_hu(player, Card("条", "2"))
print(f"   鸡胡自摸，是否能胡牌: {can_hu_self}")
assert can_hu_self == True, "鸡胡自摸测试失败"

# 点炮情况
player.drawn_card = None
can_hu_other = hu_rules.can_hu(player, Card("条", "2"))
print(f"   鸡胡点炮，是否能胡牌: {can_hu_other}")
assert can_hu_other == False, "鸡胡点炮测试失败"
print("   ✅ 鸡胡只能自摸测试通过")

# 测试4：杠上开花
print("\n4. 测试杠上开花：")
player.hand = [
    Card("万", "1"), Card("万", "2"), Card("万", "3"),
    Card("万", "4"), Card("万", "5"), Card("万", "6"),
    Card("万", "7"), Card("万", "8"), Card("万", "9"),
    Card("筒", "1"), Card("筒", "1"), Card("筒", "1"),
    Card("筒", "1")
]
player.last_action = "暗杠"  # 上一次操作是杠牌
player.drawn_card = Card("条", "2")
player.hand.append(Card("条", "2"))  # 杠后摸到的牌

# 检查是否是杠上开花
is_gang_shang_kai_hua = hu_rules._is_gang_shang_kai_hua(player, Card("条", "2"))
print(f"   杠后摸牌胡牌，是否是杠上开花: {is_gang_shang_kai_hua}")
assert is_gang_shang_kai_hua == True, "杠上开花测试失败"
print("   ✅ 杠上开花测试通过")

print("\n" + "=" * 50)
print("所有测试通过！基础行牌规则和胡牌逻辑已正确实现。")