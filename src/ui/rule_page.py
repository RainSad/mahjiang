from abc import ABC, abstractmethod
from PyQt5.QtWidgets import QWidget
from src.core.data.action import Action


class RulePage(ABC):
    """规则页面基类：定义规则专用UI页面的接口
    
    每个麻将规则可以有自己的UI页面，展示规则特有的信息和控制。
    页面负责：
    1. 渲染规则特有的状态信息（定缺、番型提示等）
    2. 为人类玩家构建动作按钮
    3. 返回玩家选择的动作
    """
    
    @abstractmethod
    def setup_ui(self, parent: QWidget):
        """初始化UI组件
        
        Args:
            parent: 父窗口widget，用于构建子组件
        """
        pass
    
    @abstractmethod
    def render_state(self, game_state):
        """根据游戏状态刷新显示
        
        Args:
            game_state: 当前游戏状态
        """
        pass
    
    @abstractmethod
    def render_actions(self, player, game_state, valid_actions: list, action_callback):
        """构建动作按钮供人类玩家选择
        
        Args:
            player: 当前玩家
            game_state: 游戏状态
            valid_actions: 可用的动作列表
            action_callback: 回调函数，接收 (action_type: str, card=None)
        """
        pass
    
    @abstractmethod
    def render_hand(self, player, action_callback):
        """渲染玩家手牌
        
        Args:
            player: 当前玩家
            action_callback: 回调函数，接收 (action_type: str, card)
        """
        pass
    
    @abstractmethod
    def reset(self):
        """重置页面状态"""
        pass
    
    @abstractmethod
    def get_widget(self) -> QWidget:
        """返回页面的顶层widget"""
        pass
