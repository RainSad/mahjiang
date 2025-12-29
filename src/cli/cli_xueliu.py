import random
from typing import List
from collections import Counter

from src.core.logic.turn_handler import TurnHandler, init_game
from src.interface.game_api import get_player_input


def _prompt_human_seat() -> str:
    wind_map = {"east": "东", "south": "南", "west": "西", "north": "北"}
    while True:
        choice = input("选择你的风位 (east/south/west/north，回车随机): ").strip().lower()
        if not choice:
            return random.choice(list(wind_map.values()))
        if choice in wind_map:
            return wind_map[choice]
        print("输入无效，请重新输入 east/south/west/north")


def _prompt_ai_strategy() -> str:
    while True:
        choice = input("选择AI策略 base/advanced (回车默认 advanced): ").strip().lower()
        if choice in ("", "advanced"):
            return "advanced"
        if choice == "base":
            return "base"
        print("输入无效，请输入 base 或 advanced")


def _build_players_config(human_wind: str, ai_strategy: str) -> List[dict]:
    winds = ["东", "南", "西", "北"]
    players = []
    for wind in winds:
        is_ai = wind != human_wind
        entry = {"name": "你" if not is_ai else f"AI-{wind}", "is_ai": is_ai}
        if is_ai:
            entry["ai_strategy"] = ai_strategy
        players.append(entry)
    return players


def _display_name(card) -> str:
    return getattr(card, "get_display_name", lambda: card.id)()


def _group_hand(hand):
    """Group hand into triplets (刻子) and sequences (顺子), then singles."""
    sorted_hand = sorted(hand, key=lambda c: (c.suit, int(c.rank) if c.rank.isdigit() else 0))
    
    # Count cards by suit
    by_suit = {}
    for c in sorted_hand:
        by_suit.setdefault(c.suit, []).append(c)
    
    groups = []
    singles = []
    
    for suit, cards in by_suit.items():
        card_list = list(cards)
        ranks = [int(c.rank) if c.rank.isdigit() else 0 for c in card_list]
        rank_count = Counter(ranks)
        
        # Find triplets (3+ same rank)
        for rank, cnt in sorted(rank_count.items()):
            if cnt >= 3:
                triplet = [c for c in card_list if int(c.rank) == rank][:3]
                groups.append(("刻子", triplet))
                for c in triplet:
                    card_list.remove(c)
        
        # Find sequences (consecutive ranks)
        card_list.sort(key=lambda c: int(c.rank) if c.rank.isdigit() else 0)
        i = 0
        while i < len(card_list) - 2:
            r1 = int(card_list[i].rank) if card_list[i].rank.isdigit() else 0
            r2 = int(card_list[i+1].rank) if card_list[i+1].rank.isdigit() else 0
            r3 = int(card_list[i+2].rank) if card_list[i+2].rank.isdigit() else 0
            
            if r2 == r1 + 1 and r3 == r2 + 1:
                groups.append(("顺子", [card_list[i], card_list[i+1], card_list[i+2]]))
                card_list = card_list[:i] + card_list[i+3:]
            else:
                i += 1
        
        singles.extend(card_list)
    
    return groups, singles


def _display_hand_grouped(player, drawn_card=None):
    """Display hand with groups highlighted and drawn card separate."""
    hand = [c for c in player.hand if c != drawn_card]
    groups, singles = _group_hand(hand)
    
    # Display groups (without indices)
    if groups:
        group_strs = []
        for group_type, cards in groups:
            group_str = " ".join(_display_name(c) for c in cards)
            group_strs.append(f"[{group_type}: {group_str}]")
        print("  " + "  ".join(group_strs))
    
    # Display singles with numbers below
    all_singles = list(singles)
    if drawn_card:
        all_singles.append(drawn_card)
    
    if all_singles:
        # Build tile row and number row
        tile_row = []
        num_row = []
        for i, card in enumerate(all_singles, 1):
            name = _display_name(card)
            marker = "(摸)" if card == drawn_card else ""
            
            # Pad to align with numbers
            tile_str = f"{name}{marker}"
            num_str = str(i)
            
            # Make them same width for alignment
            width = max(len(tile_str), len(num_str))
            tile_row.append(tile_str.ljust(width))
            num_row.append(num_str.ljust(width))
        
        # Print in rows of 7
        for start in range(0, len(tile_row), 7):
            print("  " + "  ".join(tile_row[start:start+7]))
            print("  " + "  ".join(num_row[start:start+7]))


def _parse_token_to_id(token: str) -> str | None:
    if not token:
        return None
    token = token.strip()
    suits = {"万", "筒", "条"}
    if len(token) == 2:
        a, b = token[0], token[1]
        if a in suits and b.isdigit():
            return f"{a}{b}"
        if b in suits and a.isdigit():
            return f"{b}{a}"
    return None


def _prompt_exchange_three(player, game_state):
    if getattr(player, "has_exchanged_three", False):
        return
    print("\n--- 换三张 ---")
    hand = sorted(player.hand, key=lambda c: (c.suit, int(c.rank) if c.rank.isdigit() else 0))
    print("你的手牌:")
    for i, card in enumerate(hand, 1):
        print(f"  {i}.{_display_name(card)}", end="  ")
        if i % 7 == 0:
            print()
    print()
    raw = input("输入要交换的牌序号，空格分隔（最多3张，回车跳过）: ").strip()
    if not raw:
        setattr(player, "has_exchanged_three", True)
        return
    tokens = raw.split()
    chosen = []
    for token in tokens[:3]:
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(hand):
                chosen.append(hand[idx])
    if not chosen:
        print("未找到有效牌，跳过换三张。")
        setattr(player, "has_exchanged_three", True)
        return
    game_state.rule.exchange_three_for_player(player, chosen, game_state)
    print("换三张完成。")


def _auto_exchange_three_for_ai(game_state):
    game_state.rule.exchange_three_auto_for_ai(game_state)


def _prompt_que_men(player):
    if getattr(player, "que_men", None):
        return
    while True:
        choice = input("选择定缺 (1=万/2=筒/3=条): ").strip()
        que_map = {"1": "万", "2": "筒", "3": "条", "万": "万", "筒": "筒", "条": "条"}
        if choice in que_map:
            player.que_men = que_map[choice]
            player.que_men_locked = True
            print(f"你选择的缺门: {player.que_men}")
            return
        print("输入无效，请输入 1/2/3 或 万/筒/条")


def _auto_set_ai_que(player):
    if getattr(player, "que_men", None):
        return
    counts = {"万": 0, "筒": 0, "条": 0}
    for c in player.hand:
        if c.suit in counts:
            counts[c.suit] += 1
    que = min(counts.items(), key=lambda x: (x[1], x[0]))[0]
    player.que_men = que
    player.que_men_locked = True


def _prompt_discard_for_human(player, game_state):
    """Prompt human to discard using numeric index."""
    hand = [c for c in player.hand if c != player.drawn_card]
    drawn = player.drawn_card
    
    # Build index map
    groups, singles = _group_hand(hand)
    all_cards = list(singles) + ([drawn] if drawn else [])
    
    while True:
        choice = input("\n输入牌序号（回车采用AI推荐）: ").strip()
        if not choice:
            return None  # Use AI recommendation
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(all_cards):
                return all_cards[idx]
        
        print("输入无效，请重新输入")

def _display_opponents_status(game_state, current_player):
    """Display opponents' discard history and meld info."""
    print("\n对手状态:")
    for p in game_state.players:
        if p == current_player:
            continue
        discards = getattr(p, "discarded_cards", [])
        melds = getattr(p, "melds", [])
        que = getattr(p, "que_men", "-")
        
        # Show basic info
        info_parts = [f"{p.position} {p.name} (缺{que})"]
        
        # Show melds
        if melds:
            meld_strs = []
            for m in melds:
                meld_type = getattr(m, "type", "")
                cards = getattr(m, "cards", [])
                if cards:
                    meld_str = "".join(_display_name(c) for c in cards[:3])
                    meld_strs.append(f"[{meld_type}:{meld_str}]")
            info_parts.append("副露: " + " ".join(meld_strs))
        
        print("  " + " | ".join(info_parts))
        
        # Show recent discards (last 10)
        if discards:
            recent = discards[-10:]
            discard_str = " ".join(_display_name(c) for c in recent)
            print(f"    弃牌: {discard_str}")
            if len(discards) > 10:
                print(f"    (共{len(discards)}张，仅显示最近10张)")

def _run_hand(seat_winds, dealer_wind, human_wind, ai_strategy):
    players_config = _build_players_config(human_wind, ai_strategy)
    options = {
        "auto_exchange_three": False,
        "seat_winds": seat_winds,
        "dealer_wind": dealer_wind,
    }
    game_state = init_game("tencent_xueliu", players_config, options=options)
    game_state.rule.allow_multiple_hu = False

    # 换三张阶段
    human = next(p for p in game_state.players if not p.is_ai)
    _prompt_exchange_three(human, game_state)
    _auto_exchange_three_for_ai(game_state)

    # 定缺阶段
    _prompt_que_men(human)
    for p in game_state.players:
        if p.is_ai:
            _auto_set_ai_que(p)
    print("\n定缺结果:")
    for p in game_state.players:
        print(f"  {p.position} {p.name}: 缺 {getattr(p, 'que_men', '-')}")

    # 主回合循环
    turn_count = 0
    while game_state.game_stage == "playing":
        current = game_state.current_player
        turn_count += 1
        
        if not current.is_ai:
            print(f"\n{'='*60}")
            print(f"第 {turn_count} 回合 | 你的回合 ({current.position})")
            print(f"{'='*60}")
            _display_opponents_status(game_state, current)
            print(f"\n你的手牌:")
            _display_hand_grouped(current, current.drawn_card)
            
            # Check valid actions (important for must_discard_que)
            valid_actions = game_state.rule.get_valid_actions(current, game_state)
            
            # Get AI recommendation
            from src.ai.strategy.decision_manager import AIDecisionManager
            manager = AIDecisionManager(game_state.rule, strategy="advanced")
            rec = manager.recommend(current, game_state)
            ai_action = rec["action"]
            reason = rec["reason"]
            
            # Display constraint or recommendation
            if "must_discard_que" in valid_actions:
                que_suit = getattr(current, "que_men", "")
                print(f"\n⚠️  定缺{que_suit}，必须先打出{que_suit}！")
                print(f"\n=== AI 推荐打 {_display_name(ai_action.card)} ===")
                print(f"理由: {reason}")
            elif ai_action and ai_action.type == "discard":
                print(f"\n=== AI 推荐打 {_display_name(ai_action.card)} ===")
                print(f"理由: {reason}")
            
            # Prompt for discard
            chosen_card = _prompt_discard_for_human(current, game_state)
            if chosen_card:
                # Create manual discard action
                from src.core.data.action import Action
                action = Action("discard", chosen_card, current)
                TurnHandler.execute_action(action, current, game_state)
            else:
                # Use AI recommendation
                action = TurnHandler.process_turn(game_state)
        else:
            action = TurnHandler.process_turn(game_state)
        
        if action:
            card_info = f" {_display_name(action.card)}" if getattr(action, "card", None) else ""
            print(f"→ {current.position} {current.name}: {action.type}{card_info}")
        else:
            print(f"→ {current.position} {current.name}: 无动作")

        # 牌墙摸空处理
        if not game_state.deck and getattr(game_state.rule, "on_deck_empty", None):
            game_state.rule.on_deck_empty(game_state)
            game_state.game_stage = "ended"

        if game_state.game_stage != "playing":
            break

    print(f"\n{'='*60}")
    print("本手结束")
    print(f"{'='*60}")
    
    winners = getattr(game_state, "winners", [])
    if winners:
        names = ", ".join(f"{w.position} {w.name}" for w in winners)
        print(f"赢家: {names}")
    else:
        print("流局（无赢家）")
    
    print("\n最终分数:")
    for p in game_state.players:
        print(f"  {p.position} {p.name}: {p.score:+d}")

    return game_state


def run_cli():
    print("=== 血流成河 CLI ===")
    human_wind = _prompt_human_seat()
    ai_strategy = _prompt_ai_strategy()

    seat_winds = ["东", "南", "西", "北"]
    dealer_wind = random.choice(seat_winds)
    print(f"首局庄家: {dealer_wind}\n")

    while True:
        gs = _run_hand(seat_winds, dealer_wind, human_wind, ai_strategy)

        # 庄家留任或传庄
        winners = getattr(gs, "winners", [])
        if winners and any(w.position == dealer_wind for w in winners):
            print(f"\n庄家 {dealer_wind} 留任")
        else:
            idx = seat_winds.index(dealer_wind)
            dealer_wind = seat_winds[(idx + 1) % len(seat_winds)]
            print(f"\n庄家轮转至: {dealer_wind}")

        cont = input("\n再来一局？(y/n，回车默认n): ").strip().lower()
        if cont != "y":
            break


if __name__ == "__main__":
    run_cli()
