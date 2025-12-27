import tkinter as tk
from src.core.data.game_state import GameState
from src.core.data.player import Player
from src.rules.tencent_common.rule import TencentCommonRule
from src.ui.mahjong_ui import MahjongUI, configure_card_styles
from src.ui.ai_integration import AIDecisionManager

class MahjongGame:
    """麻将游戏主控制器"""
    
    def __init__(self):
        # 初始化游戏规则
        self.rule = TencentCommonRule()
        
        # 初始化AI决策管理器
        self.ai_manager = AIDecisionManager()
        
        # 创建游戏状态
        self.game_state = self._create_initial_game_state()
        
        # 初始化GUI
        self.root = tk.Tk()
        configure_card_styles(self.root)
        self.ui = MahjongUI(self.root, self.game_state)
        
        # 绑定事件处理
        self.ui.on_player_action = self._handle_player_action
        
        # 初始化AI推荐
        self._update_ai_recommendation()
    
    def _create_initial_game_state(self):
        """创建初始游戏状态"""
        # 创建玩家
        players = [
            Player("北家", "ai"),
            Player("东家", "ai"),
            Player("南家", "human"),  # 当前玩家
            Player("西家", "ai")
        ]
        
        # 创建游戏状态
        game_state = GameState(players, self.rule)
        
        # 初始化牌组和手牌
        game_state.initialize_game()
        
        return game_state
    
    def _handle_player_action(self, action_type, card=None):
        """处理玩家操作
        
        Args:
            action_type: 操作类型
            card: 相关的牌
        """
        print(f"玩家操作: {action_type}, 牌: {card}")
        
        # 执行游戏逻辑
        # TODO: 实现完整的游戏逻辑
        
        # 更新AI推荐
        self._update_ai_recommendation()
        
        # 重新渲染界面
        self.ui.update_game_state(self.game_state)
    
    def _update_ai_recommendation(self):
        """更新AI推荐"""
        current_player = self.game_state.players[self.game_state.current_player_index]
        if current_player.type == "human":  # 只有人类玩家才显示AI推荐
            best_card, reason = self.ai_manager.get_best_discard(current_player, self.game_state)
            self.ui.set_ai_recommendation(best_card, reason)
    
    def run(self):
        """运行游戏"""
        self.root.mainloop()

if __name__ == "__main__":
    game = MahjongGame()
    game.run()
