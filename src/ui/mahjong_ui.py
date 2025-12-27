import tkinter as tk
from tkinter import ttk
from src.ui.base_ui import BaseUI
from src.core.data.game_state import GameState
from src.core.data.card import Card
import math

class MahjongUI(BaseUI):
    """麻将游戏主界面"""
    
    def __init__(self, root: tk.Tk, game_state: GameState):
        super().__init__(root, game_state)
        self.card_images = {}
        self.current_recommendation = None
        self.recommendation_reason = ""
        self._load_card_images()
        self._create_widgets()
        
    def _load_card_images(self):
        """加载牌的图片（模拟实现，实际项目中需要真实图片）"""
        # 这里使用文本模拟牌的图片
        for suit in ['万', '筒', '条']:
            for rank in range(1, 10):
                card_id = f"{suit}{rank}"
                self.card_images[card_id] = card_id
        
        for suit in ['风']:
            for rank in ['东', '南', '西', '北']:
                card_id = f"{suit}{rank}"
                self.card_images[card_id] = card_id
        
        for suit in ['箭']:
            for rank in ['中', '发', '白']:
                card_id = f"{suit}{rank}"
                self.card_images[card_id] = card_id
        
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部状态栏
        self.status_bar = ttk.Label(self.main_frame, text="准备开始游戏", font=("Arial", 12))
        self.status_bar.pack(fill=tk.X, pady=5)
        
        # 中央游戏区域
        self.game_area = ttk.Frame(self.main_frame)
        self.game_area.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 玩家位置布局（东南西北）
        self.north_player_frame = ttk.Frame(self.game_area, height=200)
        self.north_player_frame.pack(fill=tk.X, side=tk.TOP)
        
        self