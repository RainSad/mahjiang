"""命令行版本入口，支持AI推荐与玩家输入。"""

from src.core.logic.turn_handler import init_game, TurnHandler
from src.core.logic.game_flow import GameFlow


def run_cli_game():
    players = [
        {"name": "玩家", "is_ai": False},
        {"name": "AI-南", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-西", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-北", "is_ai": True, "ai_strategy": "advanced"},
    ]
    game_state = init_game("tencent_common", players)
    flow = GameFlow(game_state)
    flow.start_game()


if __name__ == "__main__":
    run_cli_game()
