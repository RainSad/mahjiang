class GameFlow:
    """游戏流程控制类"""
    
    def __init__(self, game_state):
        self.game_state = game_state
    
    def start_game(self):
        """开始游戏"""
        self.game_state.game_stage = "playing"
        
        # 循环处理回合，直到游戏结束
        while self.game_state.game_stage == "playing":
            self.process_round()
    
    def process_round(self):
        """处理一局游戏"""
        from src.core.logic.turn_handler import TurnHandler
        
        # 处理当前玩家的回合
        action = TurnHandler.process_turn(self.game_state)
        
        # 如果是胡牌操作，游戏结束
        if action.type == "hu":
            self.end_game()
    
    def end_game(self):
        """结束游戏"""
        self.game_state.game_stage = "ended"
        
        # 打印游戏结果
        self.print_game_result()
    
    def print_game_result(self):
        """打印游戏结果"""
        print("\n游戏结束！")
        print(f"赢家: {self.game_state.winner.name}")
        print(f"场风: {self.game_state.wind}")
        print(f"局数: {self.game_state.round_number}")
        
        print("\n玩家分数:")
        for player in self.game_state.players:
            print(f"{player.name}: {player.score} 分")