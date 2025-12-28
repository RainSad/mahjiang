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
        self.root.title(f"Mahjong - {game_state.rule_name}")
        self.decision_manager = AIDecisionManager(game_state.rule, strategy="advanced")

        # 定缺状态
        self.dingque_completed = False
        self._pending_dingque = []
        self._dingque_window = None
        self._dingque_timer_id = None
        self._dingque_seconds = 0

        self.recommend_var = tk.StringVar(value="推荐：等待更新")
        self.risk_text = tk.StringVar(value="风险分析：")

        self._build_layout()
        self._setup_dingque()
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

        # 比分与杠明细
        self.summary_frame = ttk.LabelFrame(self.root, text="比分 / 杠明细")
        self.summary_frame.grid(row=3, column=0, columnspan=3, sticky="ew", padx=5, pady=6)
        self.summary_labels = {}
        for p in self.game_state.players:
            lbl = ttk.Label(self.summary_frame, text="")
            lbl.pack(anchor="w")
            self.summary_labels[p.name] = lbl

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
        self._refresh_summary()

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

        # 定缺标记
        if getattr(player, 'que_men', None):
            ttk.Label(frame, text=f"缺: {player.que_men}").pack(anchor="w")

    def _on_card_click(self, player, card):
        """玩家点击手牌时，执行打牌并推进回合。"""
        if self.game_state.current_player != player:
            return
        # 血流定缺：必须先出缺门牌
        must_discard_que = hasattr(self.game_state.rule, "must_discard_que_men") and self.game_state.rule.must_discard_que_men(player)
        if must_discard_que and getattr(player, "que_men", None) and card.suit != player.que_men:
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
            # 等待定缺完成再开始血流模式
            if getattr(self.game_state.rule, "allow_multiple_hu", False) and not self.dingque_completed:
                time.sleep(0.2)
                continue
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
                    else:
                        # 牌墙为空：结算并结束游戏
                        if hasattr(self.game_state.rule, 'on_deck_empty'):
                            self.game_state.rule.on_deck_empty(self.game_state)
                        self.game_state.game_stage = "ended"
                        self._render_settlement()
                        break
                # 给UI时间等待用户点击
                time.sleep(0.3)
            self.refresh_ui()
        self.recommend_var.set("对局结束")
        # 展示结算明细
        self._render_settlement()

    def _render_settlement(self):
        """在UI中展示结算明细（查花猪/查大叫/退税）"""
        logs = getattr(self.game_state, 'settlement_logs', [])
        if not logs:
            self._refresh_summary()
            return
        # 创建或更新一个结算区域
        if not hasattr(self, '_settlement_frame'):
            self._settlement_frame = ttk.LabelFrame(self.root, text="结算明细")
            self._settlement_frame.grid(row=4, column=0, columnspan=3, pady=6, padx=5, sticky="ew")
        # 清理旧内容
        for child in self._settlement_frame.winfo_children():
            child.destroy()
        # 渲染明细
        for item in logs[:50]:  # 限制显示条数
            text = f"{item.get('type')}：{item.get('from')} → {item.get('to')} +{item.get('amount')}"
            detail = item.get('detail')
            if detail:
                text += f"（{detail}）"
            ttk.Label(self._settlement_frame, text=text).pack(anchor="w")
        self._refresh_summary()

    def _refresh_summary(self):
        """同步比分/杠明细区域"""
        if not hasattr(self, "summary_labels"):
            return
        for p in self.game_state.players:
            gain = getattr(p, "total_gang_gain", 0)
            loss = getattr(p, "total_gang_loss", 0)
            que = getattr(p, "que_men", "-")
            text = f"{p.position} {p.name} 分:{p.score} 杠+{gain}/-{loss} 缺:{que}"
            self.summary_labels[p.name].config(text=text)

    # ==== 定缺 ==== #
    def _setup_dingque(self):
        if self.game_state.rule_name != "tencent_xueliu":
            self.dingque_completed = True
            return
        # AI 玩家自动选择最少牌花色
        for p in self.game_state.players:
            if p.is_ai:
                p.que_men = self._least_suit(p)
        self._pending_dingque = [p for p in self.game_state.players if not p.is_ai]
        if not self._pending_dingque:
            self.dingque_completed = True
            return
        self._prompt_next_dingque()

    def _prompt_next_dingque(self):
        if self._dingque_window:
            self._dingque_window.destroy()
            self._dingque_window = None
        if not self._pending_dingque:
            self.dingque_completed = True
            return
        player = self._pending_dingque.pop(0)
        self._dingque_seconds = 12
        win = tk.Toplevel(self.root)
        win.title(f"为 {player.name} 选择缺门")
        ttk.Label(win, text=f"为 {player.name} 选择缺门 (万/筒/条)").pack(pady=6)
        timer_label = ttk.Label(win, text=f"超时自动选择最少牌花色: {self._dingque_seconds}s")
        timer_label.pack(pady=4)

        def choose(suit):
            player.que_men = suit
            self._cancel_timer()
            win.destroy()
            self._dingque_window = None
            self._prompt_next_dingque()

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=8)
        for suit in ["万", "筒", "条"]:
            ttk.Button(btn_frame, text=suit, width=6, command=lambda s=suit: choose(s)).pack(side="left", padx=4)

        self._dingque_window = win

        def tick():
            self._dingque_seconds -= 1
            if self._dingque_seconds <= 0:
                choose(self._least_suit(player))
                return
            timer_label.config(text=f"超时自动选择最少牌花色: {self._dingque_seconds}s")
            self._dingque_timer_id = self.root.after(1000, tick)

        self._dingque_timer_id = self.root.after(1000, tick)

    def _cancel_timer(self):
        if self._dingque_timer_id:
            self.root.after_cancel(self._dingque_timer_id)
            self._dingque_timer_id = None

    def _least_suit(self, player):
        counts = {"万": 0, "筒": 0, "条": 0}
        for c in player.hand:
            if c.suit in counts:
                counts[c.suit] += 1
        # 选择数量最少的花色，数量相同时按 万-筒-条 顺序
        return min(counts.items(), key=lambda item: (item[1], ["万", "筒", "条"].index(item[0])))[0]


def run_ui_game(rule_name: str = "tencent_common"):
    """快速启动一局带GUI的麻将，默认大众规则，可指定血流"""
    from src.core.logic.turn_handler import init_game

    players = [
        {"name": "玩家", "is_ai": False},
        {"name": "AI-南", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-西", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-北", "is_ai": True, "ai_strategy": "advanced"},
    ]
    game_state = init_game(rule_name, players)
    ui = MahjongUI(game_state)
    ui.start()


if __name__ == "__main__":
    run_ui_game()
