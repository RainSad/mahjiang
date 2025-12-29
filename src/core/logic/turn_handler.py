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
        # 若牌墙为空，仍允许继续本回合（可能发生点炮等），结算由UI或外部流程触发
        
        # 标记天胡/地胡条件
        if getattr(game_state, 'first_turn', False):
            if current_player.is_dealer:
                current_player.is_tian_hu_candidate = True
            else:
                current_player.is_di_hu_candidate = True
            game_state.first_turn = False
        
        # 2. 检查是否可以自摸胡牌
        if rule.can_hu(current_player, drawn_card):
            # 确认天胡/地胡
            if getattr(current_player, 'is_tian_hu_candidate', False):
                current_player.is_tian_hu = True
            elif getattr(current_player, 'is_di_hu_candidate', False):
                current_player.is_di_hu = True
            current_player.is_tian_hu_candidate = False
            current_player.is_di_hu_candidate = False
            
            action = Action("hu", drawn_card)
            TurnHandler.execute_action(action, current_player, game_state)
            # 血流模式不结束游戏，继续从胡家下家开始
            if getattr(rule, "allow_multiple_hu", False):
                game_state.current_player = current_player.next_player
            return action
        
        # 3. 获取有效操作列表
        valid_actions = rule.get_valid_actions(current_player, game_state)
        
        # 4. AI决策或玩家输入
        if current_player.is_ai:
            from src.ai.strategy.decision import AI_Decision
            ai_decision = AI_Decision(current_player.ai_strategy, rule)
            # 定缺必须先出缺门牌
            if "must_discard_que" in valid_actions:
                que_men = getattr(current_player, "que_men", None)
                que_card = next((c for c in current_player.hand if c.suit == que_men), None)
                if que_card:
                    action = Action("discard", que_card, from_player=current_player)
                else:
                    action = ai_decision.make_decision(current_player, game_state, valid_actions)
            else:
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
            multi = getattr(rule, "allow_multiple_hu", False)
            if multi:
                hu_players = []
                for player in game_state.players:
                    if player != current_player and rule.can_hu(player, action.card):
                        hu_action = Action("hu", action.card, current_player)
                        TurnHandler.execute_action(hu_action, player, game_state)
                        hu_players.append(player)
                if hu_players:
                    # 丢弃的牌被吃胡，移除弃牌并从最后一家胡的下家继续
                    if game_state.discard_pile and game_state.discard_pile[-1] == action.card:
                        game_state.discard_pile.pop()
                    game_state.last_discarded_card = None
                    if hasattr(rule, "handle_call_transfer"):
                        for hp in hu_players:
                            rule.handle_call_transfer(hp, current_player)
                    game_state.current_player = hu_players[-1].next_player
                    return hu_action
            else:
                for player in game_state.players:
                    if player != current_player and rule.can_hu(player, action.card):
                        hu_action = Action("hu", action.card, current_player)
                        TurnHandler.execute_action(hu_action, player, game_state)
                        if hasattr(rule, "handle_call_transfer"):
                            rule.handle_call_transfer(player, current_player)
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
                # 记录已打出的牌（用于天命花猪检查）
                if not hasattr(player, 'discarded_cards'):
                    player.discarded_cards = []
                player.discarded_cards.append(action.card)
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
                        if hasattr(rule, "score_rules") and hasattr(rule.score_rules, "settle_gang_payment"):
                            rule.score_rules.settle_gang_payment(player, "补杠", None, game_state)
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
                    if hasattr(rule, "score_rules") and hasattr(rule.score_rules, "settle_gang_payment"):
                        rule.score_rules.settle_gang_payment(player, "明杠", from_action.from_player, game_state)
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
                    if hasattr(rule, "score_rules") and hasattr(rule.score_rules, "settle_gang_payment"):
                        rule.score_rules.settle_gang_payment(player, "暗杠", None, game_state)
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
        # 记录赢家
        if player not in game_state.winners:
            game_state.winners.append(player)
        if not game_state.winner:
            game_state.winner = player

        # 计算分数
        if action.type == "hu":
            score = game_state.rule.calculate_score(player, action.card)
            player.score += score

        # 血流模式不结束游戏，普通模式直接结束
        if getattr(game_state.rule, "allow_multiple_hu", False):
            game_state.last_discarded_card = None
        else:
            game_state.game_stage = "ended"

        # 呼叫转移：胡牌后再执行一次，确保自摸杠上炮场景
        if action.from_player and hasattr(game_state.rule, "handle_call_transfer"):
            game_state.rule.handle_call_transfer(player, action.from_player)

def init_game(rule_name: str, players_config: list, options: dict | None = None):
    """初始化游戏，并按 rule_name 选择规则实现。

    options 支持：
    - auto_exchange_three: 血流是否自动换三张（默认 True）
    - seat_winds: 玩家座次列表（长度与玩家数一致），默认 ["东","南","西","北"]
    - dealer_wind: 庄风，默认 seat_winds[0]
    """
    from src.core.data.game_state import GameState
    from src.core.data.player import Player
    from src.rules.tencent_common.rule import TencentCommonRule
    from src.rules.tencent_xueliu.rule import TencentXueliuRule

    # 1. 创建游戏状态
    game_state = GameState(rule_name)

    # 2. 加载规则
    rule_map = {
        "tencent_common": TencentCommonRule,
        "tencent_xueliu": TencentXueliuRule,
    }
    if rule_name not in rule_map:
        raise ValueError(f"未知规则: {rule_name}")
    game_state.rule = rule_map[rule_name]()
    # 可选项：用于GUI控制规则行为（如血流是否自动换三张）
    options = options or {}
    if rule_name == "tencent_xueliu":
        setattr(game_state.rule, "auto_exchange_three", options.get("auto_exchange_three", True))

    # 3. 创建玩家
    for config in players_config:
        player = Player(config["name"], config["is_ai"])
        if config.get("ai_strategy"):
            player.ai_strategy = config["ai_strategy"]  # TODO: 实现AI策略加载
        game_state.players.append(player)

    # 4. 设置玩家位置和邻居关系（支持自定义座次/庄风）
    positions = ['东', '南', '西', '北']
    seat_winds = options.get("seat_winds") if options else None
    if not seat_winds or len(seat_winds) != len(game_state.players):
        seat_winds = positions[: len(game_state.players)]

    dealer_wind = options.get("dealer_wind") if options else None
    if dealer_wind is None:
        dealer_wind = seat_winds[0]

    # 更新场风为庄风，保持默认兼容性
    game_state.wind = dealer_wind

    for i, player in enumerate(game_state.players):
        player.position = seat_winds[i]
        player.is_dealer = (player.position == dealer_wind)
        player.men_feng = seat_winds[i]
        player.chang_feng = game_state.wind
        player.previous_player = game_state.players[(i - 1) % len(game_state.players)]
        player.next_player = game_state.players[(i + 1) % len(game_state.players)]
        player.game_state = game_state

    # 5. 洗牌和发牌
    shuffle_and_deal(game_state)

    # 5.5 血流换三张：默认自动，GUI可通过 options 关闭以进行人工选择
    if hasattr(game_state.rule, "exchange_three") and getattr(game_state.rule, "auto_exchange_three", True):
        game_state.rule.exchange_three(game_state)

    # 6. 设置游戏阶段为进行中
    dealer_player = next((p for p in game_state.players if getattr(p, "is_dealer", False)), game_state.players[0])
    game_state.current_player = dealer_player  # 庄家先出牌
    game_state.game_stage = "playing"
    game_state.first_turn = True  # 标记首轮，用于天胡/地胡判定

    return game_state