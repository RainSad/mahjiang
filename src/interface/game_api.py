"""游戏API接口 - 处理玩家输入和输出"""

from src.core.data.action import Action


def get_player_input(player, game_state, valid_actions):
    """获取玩家输入（当前为占位实现）
    
    Args:
        player: 当前玩家
        game_state: 游戏状态
        valid_actions: 有效操作列表
    
    Returns:
        Action: 玩家选择的操作
    """
    # TODO: 实现实际的玩家输入界面
    # 这是一个占位实现，返回打出摸到的牌
    if player.drawn_card:
        return Action("discard", player.drawn_card)
    
    # 如果没有摸到牌，从手牌中选择第一张打出
    if player.hand:
        return Action("discard", player.hand[0])
    
    # 默认过操作
    return Action("pass")


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
