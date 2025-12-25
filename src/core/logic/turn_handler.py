from src.core.data.action import Action
from src.core.logic.deck_manager import DeckManager, shuffle_and_deal

class TurnHandler:
    """回合处理类"""
    
    @staticmethod
    def process_turn(game_state):
        """处理单个玩家的回合
        
        Args:
            game_state: 游戏状态实例
        
        Returns:
            玩家执行的操作
        """
        current_player = game_state.current_player
        rule = game_state.rule
        
        # 1. 摸牌
        drawn_card = DeckManager.draw_card(game_state)
        current_player.drawn_card = drawn_card
        
        # 2. 检查是否可以自摸胡牌
        if rule.can_hu(current_player, drawn_card):
            action = Action("hu", drawn_card)
            TurnHandler.execute_action(action, current_player, game_state)
            return action
        
        # 3. 获取有效操作列表
        valid_actions = rule.get_valid_actions(current_player, game_state)
        
        # 4. AI决策或玩家输入
        if current_player.is_ai:
            from src.ai.decision import AI_Decision
            ai_decision = AI_Decision(current_player.ai_strategy, rule)
            action = ai_decision.make_decision(current_player, game_state, valid_actions)
        else:
            from src.interface.game_api import get_player_input
            action = get_player_input(current_player, game_state, valid_actions)
        
        # 5. 执行操作
        TurnHandler.execute_action(action, current_player, game_state)
        
        # 6. 检查是否有其他玩家可以胡牌（如果是打牌操作）
        if action.type == "discard" and rule.allow_other_hu:
            for player in game_state.players:
                if player != current_player and rule.can_hu(player, action.card):
                    hu_action = Action("hu", action.card, current_player)
                    TurnHandler.execute_action(hu_action, player, game_state)
                    return hu_action
        
        # 7. 切换到下一个玩家
        TurnHandler.switch_player(game_state)
        
        return action
    
    @staticmethod
    def execute_action(action, player, game_state):
        """执行玩家操作
        
        Args:
            action: 操作实例
            player: 执行操作的玩家
            game_state: 游戏状态实例
        """
        rule = game_state.rule
        
        if action.type == "draw":
            # 摸牌操作已经在process_turn中处理
            pass
        elif action.type == "discard":
            # 打牌
            if action.card in player.hand:
                player.hand.remove(action.card)
                DeckManager.discard_card(game_state, action.card)
                action.from_player = player
        elif action.type == "chow":
            # 吃牌
            # TODO: 实现吃牌逻辑
            pass
        elif action.type == "pong":
            # 碰牌
            # TODO: 实现碰牌逻辑
            pass
        elif action.type == "kong":
            # 杠牌
            # TODO: 实现杠牌逻辑
            pass
        elif action.type == "hu":
            # 胡牌
            TurnHandler.handle_hu(action, player, game_state)
    
    @staticmethod
    def switch_player(game_state):
        """切换到下一个玩家
        
        Args:
            game_state: 游戏状态实例
        """
        current_player = game_state.current_player
        game_state.current_player = current_player.next_player
    
    @staticmethod
    def handle_hu(action, player, game_state):
        """处理胡牌
        
        Args:
            action: 胡牌操作
            player: 胡牌的玩家
            game_state: 游戏状态实例
        """
        # 设置游戏结束
        game_state.game_stage = "ended"
        game_state.winner = player
        
        # 计算分数
        if action.type == "hu":
            score = game_state.rule.calculate_score(player, action.card)
            player.score += score

def init_game(rule_name: str, players_config: list):
    """初始化游戏
    
    Args:
        rule_name: 使用的规则名称
        players_config: 玩家配置列表
    
    Returns:
        初始化后的游戏状态
    """
    from src.core.data.game_state import GameState
    from src.core.data.player import Player
    from src.rules.tencent_common.rule import TencentCommonRule
    
    # 1. 创建游戏状态
    game_state = GameState(rule_name)
    
    # 2. 加载规则
    # TODO: 实现规则加载逻辑，支持根据rule_name动态加载
    rule = TencentCommonRule()
    game_state.rule = rule
    
    # 3. 创建玩家
    for config in players_config:
        player = Player(config["name"], config["is_ai"])
        if config.get("ai_strategy"):
            player.ai_strategy = config["ai_strategy"]  # TODO: 实现AI策略加载
        game_state.players.append(player)
    
    # 4. 设置玩家位置和邻居关系
    positions = ['东', '南', '西', '北']
    for i, player in enumerate(game_state.players):
        player.position = positions[i]
        player.is_dealer = (i == 0)  # 第一个玩家为庄家
        player.previous_player = game_state.players[(i - 1) % len(game_state.players)]
        player.next_player = game_state.players[(i + 1) % len(game_state.players)]
    
    # 5. 洗牌和发牌
    shuffle_and_deal(game_state)
    
    # 6. 设置游戏阶段为进行中
    game_state.current_player = game_state.players[0]  # 庄家先出牌
    game_state.game_stage = "playing"
    
    return game_state