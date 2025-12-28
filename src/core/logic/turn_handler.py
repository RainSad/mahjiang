from src.core.data.action import Action, Meld
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
            from src.ai.strategy.decision import AI_Decision
            ai_decision = AI_Decision(current_player.ai_strategy, rule)
            action = ai_decision.make_decision(current_player, game_state, valid_actions)
        else:
            from src.interface.game_api import get_player_input
            action = get_player_input(current_player, game_state, valid_actions)
        
        # 5. 执行操作
        TurnHandler.execute_action(action, current_player, game_state)

        # 补花/杠后需要继续当前玩家的回合（补牌后再决策）
        if action and action.type in ["kong", "flower"]:
            return TurnHandler.process_turn(game_state)
        
        # 6. 检查是否有其他玩家可以胡牌（如果是打牌操作）
        if action and action.type == "discard" and rule.allow_other_hu:
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
                action.from_player = player
                DeckManager.discard_card(game_state, action)
            player.last_action = "出牌"
            player.drawn_card = None
            player.consecutive_gang_count = 0
        elif action.type == "chow":
            # 吃牌：使用上家弃牌与手牌组成顺子
            from_action = game_state.last_discarded_card
            target_card = action.card or (from_action.card if from_action else None)
            if not target_card:
                return
            # 找到任意可用组合
            combos = []
            current_rank = int(target_card.rank)
            candidates = {
                (current_rank - 2, current_rank - 1),
                (current_rank - 1, current_rank + 1),
                (current_rank + 1, current_rank + 2),
            }
            for a, b in candidates:
                needed = {str(a), str(b)}
                if all(any(c.suit == target_card.suit and c.rank == r for c in player.hand) for r in needed):
                    combos.append(needed)
            if combos:
                use = combos[0]
                used_cards = []
                for r in use:
                    for c in player.hand:
                        if c.suit == target_card.suit and c.rank == r:
                            used_cards.append(c)
                            player.hand.remove(c)
                            break
                meld_cards = used_cards + [target_card]
                player.melds.append(Meld("吃", meld_cards, from_player=getattr(from_action, "from_player", None)))
                player.last_action = "吃"
                player.consecutive_gang_count = 0
                if game_state.discard_pile and game_state.discard_pile[-1] == target_card:
                    game_state.discard_pile.pop()
                game_state.last_discarded_card = None
        elif action.type == "pong":
            from_action = game_state.last_discarded_card
            target_card = action.card or (from_action.card if from_action else None)
            if not target_card:
                return
            needed = [c for c in player.hand if c == target_card][:2]
            if len(needed) == 2:
                for c in needed:
                    player.hand.remove(c)
                player.melds.append(Meld("碰", needed + [target_card], from_player=getattr(from_action, "from_player", None)))
                player.last_action = "碰"
                player.consecutive_gang_count = 0
                if game_state.discard_pile and game_state.discard_pile[-1] == target_card:
                    game_state.discard_pile.pop()
                game_state.last_discarded_card = None
        elif action.type == "kong":
            from_action = game_state.last_discarded_card
            target_card = action.card or (from_action.card if from_action else None)
            if not target_card:
                return

            # 补杠：已碰的面子加一张
            for meld in player.melds:
                if getattr(meld, "type", "") == "碰" and any(c == target_card for c in getattr(meld, "cards", [])):
                    if target_card in player.hand:
                        player.hand.remove(target_card)
                        meld.cards.append(target_card)
                        meld.type = "补杠"
                        player.last_action = "补杠"
                        player.consecutive_gang_count = max(player.consecutive_gang_count, 1)
                        break
            else:
                count = sum(1 for c in player.hand if c == target_card)
                if from_action and from_action.from_player is not None and count >= 3:
                    # 明杠：别人弃牌 + 自己3张
                    used = []
                    for _ in range(3):
                        card_obj = next(c for c in player.hand if c == target_card)
                        player.hand.remove(card_obj)
                        used.append(card_obj)
                    player.melds.append(Meld("明杠", used + [target_card], from_player=from_action.from_player, concealed=False))
                    player.last_action = "明杠"
                    # 接杠：继承连杠次数
                    inherited = getattr(from_action.from_player, "consecutive_gang_count", 0)
                    player.consecutive_gang_count = inherited + 1
                elif not from_action and count == 4:
                    # 暗杠：手里四张
                    used = []
                    for _ in range(4):
                        card_obj = next(c for c in player.hand if c == target_card)
                        player.hand.remove(card_obj)
                        used.append(card_obj)
                    player.melds.append(Meld("暗杠", used, concealed=True))
                    player.last_action = "暗杠"
                    player.consecutive_gang_count += 1
                else:
                    return

            # 杠后补牌（补3取1）
            replacement = DeckManager.draw_replacement(game_state)
            player.drawn_card = replacement
            if replacement:
                player.hand.append(replacement)
            player.last_action = player.last_action or "杠牌"
            player.consecutive_gang_count = max(player.consecutive_gang_count, 1)
            if game_state.discard_pile and game_state.discard_pile[-1] == target_card:
                game_state.discard_pile.pop()
            game_state.last_discarded_card = None
        elif action.type == "hu":
            # 胡牌
            TurnHandler.handle_hu(action, player, game_state)
        elif action.type == "flower":
            flowers = [action.card] if action.card else [c for c in player.hand if c.suit == "花"]
            if not flowers:
                return
            for f in flowers:
                if f in player.hand:
                    player.hand.remove(f)
                    player.melds.append(Meld("补花", [f], concealed=False))
                    player.changed_flower_count = getattr(player, "changed_flower_count", 0) + 1
                    player.last_action = "补花"
                    player.consecutive_gang_count += 1
                    # 补花后补牌
                    replacement = DeckManager.draw_replacement(game_state)
                    player.drawn_card = replacement
                    if replacement:
                        player.hand.append(replacement)
    
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
        player.men_feng = positions[i]
        player.chang_feng = game_state.wind
        player.previous_player = game_state.players[(i - 1) % len(game_state.players)]
        player.next_player = game_state.players[(i + 1) % len(game_state.players)]
        player.game_state = game_state
    
    # 5. 洗牌和发牌
    shuffle_and_deal(game_state)
    
    # 6. 设置游戏阶段为进行中
    game_state.current_player = game_state.players[0]  # 庄家先出牌
    game_state.game_stage = "playing"
    
    return game_state