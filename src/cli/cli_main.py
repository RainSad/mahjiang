import argparse
from typing import List

from src.core.logic.turn_handler import TurnHandler, init_game


def _parse_args():
	parser = argparse.ArgumentParser(description="Mahjong CLI - choose rule and seats")
	parser.add_argument(
		"--rule",
		choices=["tencent_common", "tencent_xueliu"],
		default="tencent_common",
		help="选择规则：tencent_common 或 tencent_xueliu",
	)
	parser.add_argument(
		"--human-seat",
		choices=["east", "south", "west", "north"],
		help="人类玩家的风位（dealer 将重置到该风位）",
	)
	parser.add_argument(
		"--ai-strategy",
		choices=["base", "advanced"],
		default="advanced",
		help="AI 出牌策略",
	)
	parser.add_argument(
		"--no-auto-exchange-three",
		action="store_true",
		help="血流模式下关闭自动换三张（默认开启）",
	)
	return parser.parse_args()


def _prompt_human_seat() -> str:
	wind_map = {"east": "东", "south": "南", "west": "西", "north": "北"}
	while True:
		choice = input("选择你的风位 (east/south/west/north，回车默认 east): ").strip().lower()
		if choice == "":
			return wind_map["east"]
		if choice in wind_map:
			return wind_map[choice]
		print("输入无效，请重新输入 east/south/west/north")


def _build_players_config(human_wind: str, ai_strategy: str) -> List[dict]:
	wind_order = ["东", "南", "西", "北"]
	players = []
	for wind in wind_order:
		is_ai = wind != human_wind
		name = "你" if wind == human_wind else f"AI-{wind}"
		entry = {"name": name, "is_ai": is_ai}
		if is_ai:
			entry["ai_strategy"] = ai_strategy
		players.append(entry)
	return players


def _maybe_handle_empty_deck(game_state):
	if game_state.game_stage != "playing":
		return
	if game_state.deck:
		return
	if hasattr(game_state.rule, "on_deck_empty"):
		game_state.rule.on_deck_empty(game_state)
	game_state.game_stage = "ended"


def _print_summary(game_state):
	print("\n对局结束！")
	if getattr(game_state, "winners", None):
		winners = ", ".join(p.name for p in game_state.winners)
		print(f"赢家: {winners}")
	else:
		print("无赢家（荒局/流局）")
	print("分数：")
	for p in game_state.players:
		print(f"  {p.position} {p.name}: {p.score}")


def run_cli():
	args = _parse_args()
	human_wind = args.human_seat
	if not human_wind:
		human_wind = _prompt_human_seat()
	else:
		human_wind = {"east": "东", "south": "南", "west": "西", "north": "北"}[args.human_seat]

	players_config = _build_players_config(human_wind, args.ai_strategy)

	options = {
		"auto_exchange_three": not args.no_auto_exchange_three,
		"seat_winds": ["东", "南", "西", "北"],
		"dealer_wind": human_wind,
	}

	game_state = init_game(args.rule, players_config, options=options)

	print(f"规则: {args.rule} | 你的风位: {human_wind} | 庄家: {human_wind}")
	print("游戏开始！\n")

	while game_state.game_stage == "playing":
		current = game_state.current_player
		action = TurnHandler.process_turn(game_state)
		if not action:
			print(f"{current.position} {current.name} -> 无动作")
		else:
			card_info = f" {action.card}" if getattr(action, "card", None) else ""
			print(f"{current.position} {current.name} -> {action.type}{card_info}")

		_maybe_handle_empty_deck(game_state)

	_print_summary(game_state)


if __name__ == "__main__":
	run_cli()
