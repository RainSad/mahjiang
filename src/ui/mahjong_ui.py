import threading
import time
import tkinter as tk
from tkinter import ttk

from src.ai.strategy.decision_manager import AIDecisionManager
from src.core.logic.turn_handler import TurnHandler
from src.core.logic.deck_manager import DeckManager


class MahjongUI:
    """Tkinter GUI，用于展示腾讯大众麻将对局与AI推荐。"""

    def __init__(self, game_state):
        self.game_state = game_state
        self.root = tk.Tk()
        self.root.title("Mahjong - Tencent Common Rule")
        self.decision_manager = AIDecisionManager(game_state.rule, strategy="advanced")

        self.recommend_var = tk.StringVar(value="推荐：等待更新")
        self.risk_text = tk.StringVar(value="风险分析：")

        self._build_layout()
        self.refresh_ui()

    def _build_layout(self):
        # 四家布局：东(底部)、北(顶部)、西(左)、南(右)
        self.frames = {}
        self.frames['north'] = ttk.LabelFrame(self.root, text="北家")
        self.frames['south'] = ttk.LabelFrame(self.root, text="东家(庄)")
        self.frames['west'] = ttk.LabelFrame(self.root, text="西家")
        self.frames['east'] = ttk.LabelFrame(self.root, text="南家")

        self.frames['north'].grid(row=0, column=1, pady=5)
        self.frames['west'].grid(row=1, column=0, padx=5)
        self.frames['east'].grid(row=1, column=2, padx=5)
        self.frames['south'].grid(row=2, column=1, pady=5)

        # 推荐区域
        rec_frame = ttk.LabelFrame(self.root, text="AI 推荐")
        rec_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        ttk.Label(rec_frame, textvariable=self.recommend_var, foreground="blue").pack(anchor="w")
        ttk.Label(rec_frame, textvariable=self.risk_text, wraplength=320, justify="left").pack(anchor="w")

    def refresh_ui(self):
        for pos, frame in self.frames.items():
            for child in frame.winfo_children():
                child.destroy()

        for player in self.game_state.players:
            self._render_player(player)

        current = self.game_state.current_player
        rec = self.decision_manager.recommend(current, self.game_state)
        action = rec['action']
        reason = rec['reason']
        self.recommend_var.set(f"{current.name} 推荐: {action.type} {action.card if action.card else ''} | {reason}")
        risk_lines = ', '.join(f"{item['card']}:{item['risk']}" for item in rec['risk'][:8])
        self.risk_text.set(f"风险分析: {risk_lines}")

    def _render_player(self, player):
        pos_map = {'东': 'south', '南': 'east', '西': 'west', '北': 'north'}
        frame_key = pos_map.get(player.position, 'south')
        frame = self.frames[frame_key]

        title = f"{player.position} {player.name} {'(庄)' if player.is_dealer else ''}"
        ttk.Label(frame, text=title).pack(anchor="w")

        # 手牌按钮
        hand_frame = ttk.Frame(frame)
        hand_frame.pack(anchor="w")
        for card in player.hand:
            btn = ttk.Button(hand_frame, text=str(card), width=4,
                             command=lambda c=card, p=player: self._on_card_click(p, c))
            btn.pack(side="left", padx=2, pady=2)

        # 副露/面子
        if getattr(player, 'melds', None):
            meld_frame = ttk.Frame(frame)
            meld_frame.pack(anchor="w")
            ttk.Label(meld_frame, text="副露:").pack(side="left")
            for meld in player.melds:
                ttk.Label(meld_frame, text=f"{meld.type}:{[str(c) for c in meld.cards]}").pack(anchor="w")

    def _on_card_click(self, player, card):
        """玩家点击手牌时，执行打牌并推进回合。"""
        if self.game_state.current_player != player:
            return
        from src.core.data.action import Action
        action = Action("discard", card, from_player=player)
        TurnHandler.execute_action(action, player, self.game_state)
        TurnHandler.switch_player(self.game_state)
        self.refresh_ui()

    def start(self):
        # 在单独线程中运行回合处理，不阻塞UI
        threading.Thread(target=self._run_game_loop, daemon=True).start()
        self.root.mainloop()

    def _run_game_loop(self):
        while self.game_state.game_stage == "playing":
            current = self.game_state.current_player
            if current.is_ai:
                # AI自动执行
                valid_actions = self.game_state.rule.get_valid_actions(current, self.game_state)
                action = self.decision_manager.ai.make_decision(current, self.game_state, valid_actions)
                TurnHandler.execute_action(action, current, self.game_state)
                if action and action.type not in ["flower", "kong"]:
                    TurnHandler.switch_player(self.game_state)
            else:
                # 人类玩家：确保已摸牌，等待点击出牌
                if current.drawn_card is None:
                    drawn = DeckManager.draw_card(self.game_state)
                    current.drawn_card = drawn
                    if drawn:
                        current.hand.append(drawn)
                # 给UI时间等待用户点击
                time.sleep(0.3)
            self.refresh_ui()
        self.recommend_var.set("对局结束")


def run_ui_game():
    """快速启动一局带GUI的腾讯大众麻将，默认一人对三AI。"""
    from src.core.logic.turn_handler import init_game

    players = [
        {"name": "玩家", "is_ai": False},
        {"name": "AI-南", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-西", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-北", "is_ai": True, "ai_strategy": "advanced"},
    ]
    game_state = init_game("tencent_common", players)
    ui = MahjongUI(game_state)
    ui.start()


if __name__ == "__main__":
    run_ui_game()
