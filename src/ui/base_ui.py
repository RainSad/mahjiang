import tkinter as tk
from abc import ABC, abstractmethod
from src.core.data.game_state import GameState

class BaseUI(ABC):
    """UI基类"""
    
    def __init__(self, root: tk.Tk, game_state: GameState):
        self.root = root
        self.game_state = game_state
        self.root.title("麻将游戏")
        self.root.geometry("1000x700")
        self.root.configure(bg="#2c3e50")
        
    @abstractmethod
    def render(self):
        """渲染游戏界面"""
        pass
    
    @abstractmethod
    def update_game_state(self, game_state: GameState):
        """更新游戏状态"""
        pass
    
    @abstractmethod
    def on_player_action(self, action_type, card=None):
        """处理玩家操作"""
        pass
    
    def show_message(self, message: str, title: str = "提示"):
        """显示消息框"""
        from tkinter import messagebox
        messagebox.showinfo(title, message)
    
    def show_error(self, message: str, title: str = "错误"):
        """显示错误框"""
        from tkinter import messagebox
        messagebox.showerror(title, message)
    
    def show_question(self, message: str, title: str = "确认") -> bool:
        """显示确认框"""
        from tkinter import messagebox
        return messagebox.askyesno(title, message)
