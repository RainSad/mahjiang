import sys
import os

# 将项目根目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.data.game_state import GameState
from src.core.data.player import Player
from src.rules.tencent_common.rule import TencentCommonRule
from src.ui.ai_integration import AIDecisionManager

class MahjongCLIGame:
    """麻将游戏命令行版本"""
    
    def __init__(self):
        # 初始化游戏规则
        self.rule = TencentCommonRule()
        
        # 初始化AI决策管理器
        self.ai_manager = AIDecisionManager()
        
        # 创建游戏状态
        self.game_state = self._create_initial_game_state()
        
        # 当前玩家索引（南家，索引为2）
        self.human_player_index = 2
    
    def _create_initial_game_state(self):
        """创建初始游戏状态"""
        # 创建玩家
        players = [
            Player("北家", is_ai=True),
            Player("东家", is_ai=True),
            Player("南家", is_ai=False),  # 当前玩家
            Player("西家", is_ai=True)
        ]
        
        # 创建游戏状态
        game_state = GameState(players, self.rule)
        
        # 初始化牌组和手牌
        game_state.initialize_game()
        
        return game_state
    
    def _display_game_state(self):
        """显示游戏状态"""
        print("=" * 60)
        print(f"当前回合: {self.game_state.current_player.name} (剩余牌数: {len(self.game_state.deck)})")
        print(f"场风: {self.game_state.wind}  局数: {self.game_state.round_number}")
        print("=" * 60)
        
        # 显示弃牌堆
        if self.game_state.discard_pile:
            discard_str = "弃牌堆: " + ", ".join([card.get_display_name() for card in self.game_state.discard_pile[-10:]])
            print(discard_str)
        
        # 显示玩家手牌
        print("\n玩家手牌:")
        for i, player in enumerate(self.game_state.players):
            if i == self.human_player_index:
                # 显示当前玩家的完整手牌
                sorted_hand = sorted(player.hand, key=lambda card: (card.suit, card.rank))
                hand_str = ", ".join([card.get_display_name() for card in sorted_hand])
                print(f"{player.name}: {hand_str}")
            else:
                # 只显示其他玩家的手牌数量
                print(f"{player.name}: 手牌数量: {len(player.hand)}")
    
    def _display_ai_recommendation(self):
        """显示AI推荐"""
        if not self.game_state.current_player.is_ai:  # 只有人类玩家才显示AI推荐
            print("\n" + "=" * 60)
            print("AI智能推荐:")
            best_card, reason = self.ai_manager.get_best_discard(self.game_state.current_player, self.game_state)
            print(f"推荐出牌: {best_card.get_display_name()}")
            print(f"推荐理由: {reason}")
            
            # 显示危险牌分析
            print("\n危险牌分析:")
            danger_cards = self.ai_manager.analyze_danger_cards(self.game_state.current_player, self.game_state)
            for card, risk in list(danger_cards.items())[:5]:  # 只显示前5个危险牌
                risk_level = "高" if risk > 0.7 else "中" if risk > 0.3 else "低"
                print(f"{card.get_display_name()}: 风险等级{risk_level} (风险值: {risk:.2f})")
            print("=" * 60)
    
    def _get_player_input(self):
        """获取玩家输入"""
        print("\n可用操作:")
        print("1. 出牌")
        print("2. 吃")
        print("3. 碰")
        print("4. 杠")
        print("5. 胡")
        
        choice = input("请选择操作(1-5): ")
        return choice
    
    def _handle_player_action(self, action_type, card=None):
        """处理玩家操作"""
        print(f"\n玩家操作: {action_type}, 牌: {card}")
        
        # 执行游戏逻辑
        # TODO: 实现完整的游戏逻辑
        
        # 更新游戏状态
        # 这里简化处理，直接切换到下一个玩家
        current_index = self.game_state.players.index(self.game_state.current_player)
        next_index = (current_index + 1) % 4
        self.game_state.current_player = self.game_state.players[next_index]
    
    def run(self):
        """运行游戏"""
        print("欢迎来到腾讯大众麻将游戏！")
        print("=" * 60)
        
        while self.game_state.game_stage == "playing":
            # 显示游戏状态
            self._display_game_state()
            
            # 显示AI推荐
            self._display_ai_recommendation()
            
            # 如果是当前玩家的回合
            if not self.game_state.current_player.is_ai:
                # 获取玩家输入
                choice = self._get_player_input()
                
                if choice == "1":
                    # 出牌操作
                    self._handle_player_discard()
                elif choice == "2":
                    # 吃牌操作
                    self._handle_player_action("chi")
                elif choice == "3":
                    # 碰牌操作
                    self._handle_player_action("peng")
                elif choice == "4":
                    # 杠牌操作
                    self._handle_player_action("gang")
                elif choice == "5":
                    # 胡牌操作
                    self._handle_player_action("hu")
                    break
                else:
                    print("无效的选择，请重新输入！")
            else:
                # AI玩家的回合，简单处理
                print(f"\n{self.game_state.current_player.name}正在思考...")
                best_card, reason = self.ai_manager.get_best_discard(self.game_state.current_player, self.game_state)
                print(f"{self.game_state.current_player.name}打出: {best_card.get_display_name()}")
                self._handle_player_action("discard", best_card)
        
        print("\n游戏结束！")
    
    def _handle_player_discard(self):
        """处理玩家出牌"""
        player = self.game_state.current_player
        sorted_hand = sorted(player.hand, key=lambda card: (card.suit, card.rank))
        
        print("\n你的手牌:")
        for i, card in enumerate(sorted_hand):
            print(f"{i+1}. {card.get_display_name()}")
        
        try:
            choice = int(input("请选择要打出的牌编号: ")) - 1
            if 0 <= choice < len(sorted_hand):
                selected_card = sorted_hand[choice]
                self._handle_player_action("discard", selected_card)
            else:
                print("无效的选择，请重新输入！")
        except ValueError:
            print("无效的输入，请输入数字！")

if __name__ == "__main__":
    game = MahjongCLIGame()
    game.run()
