"""游戏API接口 - 处理玩家输入和输出"""

from src.core.data.action import Action
from src.ai.strategy.decision_manager import AIDecisionManager


def get_player_input(player, game_state, valid_actions):
    """获取玩家输入（命令行版本）。提供AI推荐和风险提示，玩家可自由选择。"""
    manager = AIDecisionManager(game_state.rule, strategy="advanced")
    rec = manager.recommend(player, game_state)
    action = rec["action"]
    reason = rec["reason"]
    risk_lines = ", ".join(f"{item['card']}: {item['risk']}" for item in rec["risk"])

    print("\n=== AI 推荐 ===")
    print(f"动作: {action.type} {action.card if action.card else ''} | 理由: {reason}")
    print(f"风险评估: {risk_lines}")
    print(f"可选操作: {valid_actions}")

    choice = input("输入操作类型(直接回车采用推荐): ").strip()
    if not choice:
        return action
    choice = choice.lower()

    if choice == "discard":
        print("你的手牌:", player.hand)
        card_id = input("输入要打出的牌(例: 万1): ").strip()
        for c in player.hand:
            if c.id == card_id:
                return Action("discard", c)
        print("未找到该牌，使用推荐")
        return action
    if choice in {"hu", "kong", "pong", "chow", "flower"}:
        target = getattr(game_state.last_discarded_card, "card", None) or player.drawn_card
        return Action(choice, target)

    return action


def display_game_state(game_state):
    """显示游戏状态（占位实现）
    
    Args:
        game_state: 游戏状态
    """
    # TODO: 实现游戏状态的可视化展示
    pass


def display_player_hand(player):
    """显示玩家手牌（占位实现）
    
    Args:
        player: 玩家对象
    """
    # TODO: 实现手牌的可视化展示
    pass


def notify_action(player, action):
    """通知操作执行（占位实现）
    
    Args:
        player: 执行操作的玩家
        action: 执行的操作
    """
    # TODO: 实现操作通知功能
    pass
