# 自动打麻将程序架构设计

## 一、项目设计目标

1. **模块化设计**：支持多种麻将规则的扩展
2. **逻辑分离**：游戏逻辑、出牌逻辑、危险牌预测等独立实现
3. **可扩展性**：便于后续添加新的麻将打法
4. **清晰的目录结构**：每个麻将打法独立存放
5. **可测试性**：便于单元测试和集成测试

## 二、目录结构设计

```
mahjiang/
├── src/
│   ├── core/                  # 核心模块（与具体规则无关）
│   │   ├── data/              # 核心数据结构
│   │   │   ├── card.py        # 牌类定义
│   │   │   ├── player.py      # 玩家类定义
│   │   │   ├── game_state.py  # 游戏状态类定义
│   │   │   └── action.py      # 操作类定义
│   │   ├── logic/             # 通用游戏逻辑
│   │   │   ├── game_flow.py   # 游戏流程控制
│   │   │   ├── deck_manager.py # 牌墙管理
│   │   │   └── turn_handler.py # 回合处理
│   │   └── utils/             # 通用工具函数
│   │       ├── logger.py      # 日志管理
│   │       └── helper.py      # 辅助函数
│   ├── rules/                 # 麻将规则模块（每种规则独立目录）
│   │   ├── base_rule.py       # 规则基类
│   │   ├── tencent_common/    # 腾讯大众麻将规则
│   │   │   ├── rule.py        # 核心规则实现
│   │   │   ├── hu_rules.py    # 胡牌规则
│   │   │   ├── action_rules.py # 操作规则
│   │   │   └── score_rules.py # 计分规则
│   │   └── guobiao/           # 国标麻将规则（预留）
│   ├── ai/                    # AI决策系统
│   │   ├── base_ai.py         # AI基类
│   │   ├── strategy/          # 策略算法
│   │   │   ├── base_strategy.py # 策略基类
│   │   │   ├── simple_strategy.py # 简单策略
│   │   │   └── advanced_strategy.py # 高级策略
│   │   ├── evaluation/        # 评估模块
│   │   │   ├── hand_evaluator.py # 手牌评估
│   │   │   ├── risk_evaluator.py # 危险牌预测
│   │   │   └── value_evaluator.py # 价值评估
│   │   └── decision.py        # 决策核心
│   ├── interface/             # 外部接口
│   │   ├── game_api.py        # 游戏控制接口
│   │   └── result_api.py      # 结果查询接口
│   └── ui/                    # 可选的用户界面
│       ├── base_ui.py         # UI基类
│       └── terminal_ui.py     # 终端界面
├── tests/                     # 测试代码
│   ├── core/                  # 核心模块测试
│   ├── rules/                 # 规则测试
│   └── ai/                    # AI模块测试
├── docs/                      # 文档
├── config/                    # 配置文件
├── requirements.txt           # 依赖列表
└── main.py                    # 程序入口
```

## 三、核心模块设计

### 1. 核心数据结构

#### Card类（src/core/data/card.py）
```python
class Card:
    def __init__(self, suit: str, rank: str):
        """牌类定义
        
        Args:
            suit: 花色（万、筒、条、风、箭）
            rank: 点数（1-9或东南西北中发白）
        """
        self.suit = suit
        self.rank = rank
        self.id = f"{suit}{rank}"  # 唯一标识
        self.is_visible = False    # 是否可见（用于暗杠）
        
    def __repr__(self):
        return self.id
        
    def __eq__(self, other):
        return self.id == other.id if other else False
        
    def __hash__(self):
        return hash(self.id)
```

#### Player类（src/core/data/player.py）
```python
class Player:
    def __init__(self, name: str, is_ai: bool = True):
        """玩家类定义
        
        Args:
            name: 玩家名称
            is_ai: 是否为AI玩家
        """
        self.name = name
        self.is_ai = is_ai
        self.hand = []              # 手牌
        self.melds = []             # 吃碰杠的牌
        self.score = 0              # 分数
        self.position = None        # 位置：东、南、西、北
        self.is_dealer = False      # 是否是庄家
        self.drawn_card = None      # 当前摸到的牌
        self.ai_strategy = None     # AI策略
        self.previous_player = None # 上家
        self.next_player = None     # 下家
```

#### GameState类（src/core/data/game_state.py）
```python
class GameState:
    def __init__(self, rule_name: str = "tencent_common"):
        """游戏状态类定义
        
        Args:
            rule_name: 使用的规则名称
        """
        self.rule_name = rule_name
        self.deck = []              # 剩余牌墙
        self.discard_pile = []      # 已打出的牌
        self.players = []           # 玩家列表
        self.current_player = None  # 当前回合玩家
        self.last_discarded_card = None  # 上一张打出的牌
        self.game_stage = "init"    # 游戏阶段：init/playing/ended
        self.winner = None          # 赢家
        self.round_number = 1       # 局数
        self.wind = "东"            # 场风
        self.rule = None            # 当前规则实例
```

#### Action类（src/core/data/action.py）
```python
class Action:
    def __init__(self, action_type: str, card: 'Card' = None, from_player=None):
        """操作类定义
        
        Args:
            action_type: 操作类型（draw/discard/chow/pong/kong/hu）
            card: 涉及的牌
            from_player: 来源玩家
        """
        self.type = action_type
        self.card = card
        self.from_player = from_player
        self.timestamp = None       # 操作时间戳
        
    def __repr__(self):
        return f"Action(type={self.type}, card={self.card}, from={self.from_player.name if self.from_player else 'None'})"
```

### 2. 规则系统设计

#### BaseRule基类（src/rules/base_rule.py）
```python
class BaseRule:
    """规则基类，定义规则接口"""
    
    def __init__(self):
        # 通用规则配置
        self.max_players = 4
        self.tiles_count = 136
        self.starting_tiles = 13
        self.dealer_extra_tile = True
        self.allow_chow = True
        self.allow_pong = True
        self.allow_kong = True
        self.allow_self_hu = True
        self.allow_other_hu = True
    
    def can_chow(self, player: 'Player', card: 'Card', from_player) -> bool:
        """判断是否可以吃牌"""
        raise NotImplementedError
    
    def can_pong(self, player: 'Player', card: 'Card', from_player) -> bool:
        """判断是否可以碰牌"""
        raise NotImplementedError
    
    def can_kong(self, player: 'Player', card: 'Card', from_player) -> bool:
        """判断是否可以杠牌"""
        raise NotImplementedError
    
    def can_hu(self, player: 'Player', card: 'Card') -> bool:
        """判断是否可以胡牌"""
        raise NotImplementedError
    
    def calculate_score(self, player: 'Player', winning_card: 'Card') -> int:
        """计算胡牌分数"""
        raise NotImplementedError
    
    def get_valid_actions(self, player: 'Player', game_state: 'GameState') -> list:
        """获取当前玩家的有效操作"""
        raise NotImplementedError
    
    def create_initial_deck(self) -> list:
        """创建初始牌组"""
        raise NotImplementedError
```

#### 腾讯大众麻将规则实现（src/rules/tencent_common/rule.py）
```python
from src.rules.base_rule import BaseRule
from src.rules.tencent_common.hu_rules import TencentHuRules
from src.rules.tencent_common.action_rules import TencentActionRules
from src.rules.tencent_common.score_rules import TencentScoreRules

class TencentCommonRule(BaseRule):
    """腾讯大众麻将规则实现"""
    
    def __init__(self):
        super().__init__()
        # 腾讯大众麻将特定规则配置
        self.allow_chow = True  # 允许吃牌
        self.allow_pong = True  # 允许碰牌
        self.allow_kong = True  # 允许杠牌
        self.max_fans = 10      # 最大番数
        self.mandatory_discard = True  # 必须有一张牌可以打出
        
        # 加载子规则
        self.hu_rules = TencentHuRules(self)
        self.action_rules = TencentActionRules(self)
        self.score_rules = TencentScoreRules(self)
    
    def can_chow(self, player: 'Player', card: 'Card', from_player) -> bool:
        """腾讯大众麻将吃牌规则"""
        return self.action_rules.can_chow(player, card, from_player)
    
    def can_pong(self, player: 'Player', card: 'Card', from_player) -> bool:
        """腾讯大众麻将碰牌规则"""
        return self.action_rules.can_pong(player, card, from_player)
    
    def can_kong(self, player: 'Player', card: 'Card', from_player) -> bool:
        """腾讯大众麻将杠牌规则"""
        return self.action_rules.can_kong(player, card, from_player)
    
    def can_hu(self, player: 'Player', card: 'Card') -> bool:
        """腾讯大众麻将胡牌规则"""
        return self.hu_rules.can_hu(player, card)
    
    def calculate_score(self, player: 'Player', winning_card: 'Card') -> int:
        """腾讯大众麻将计分规则"""
        return self.score_rules.calculate_score(player, winning_card)
    
    def get_valid_actions(self, player: 'Player', game_state: 'GameState') -> list:
        """获取当前玩家的有效操作"""
        return self.action_rules.get_valid_actions(player, game_state)
    
    def create_initial_deck(self) -> list:
        """创建腾讯大众麻将初始牌组"""
        # 实现创建136张牌的逻辑
        from src.core.data.card import Card
        deck = []
        
        # 序数牌（万、筒、条）
        for suit in ['万', '筒', '条']:
            for rank in range(1, 10):
                for _ in range(4):
                    deck.append(Card(suit, str(rank)))
        
        # 风牌
        for suit in ['风']:
            for rank in ['东', '南', '西', '北']:
                for _ in range(4):
                    deck.append(Card(suit, rank))
        
        # 箭牌
        for suit in ['箭']:
            for rank in ['中', '发', '白']:
                for _ in range(4):
                    deck.append(Card(suit, rank))
        
        return deck
```

### 3. AI决策系统设计

#### 危险牌预测模块（src/ai/evaluation/risk_evaluator.py）
```python
class RiskEvaluator:
    """危险牌预测模块"""
    
    def __init__(self, rule: 'BaseRule'):
        self.rule = rule
        
    def evaluate_card_risk(self, card: 'Card', player: 'Player', game_state: 'GameState') -> float:
        """评估打出某张牌的风险
        
        Returns:
            风险值（0-1，越高越危险）
        """
        # 1. 计算牌的出现概率
        card_probability = self._calculate_card_probability(card, game_state)
        
        # 2. 评估对手听牌可能性
        opponent_hu_probability = self._estimate_opponent_hu_probability(player, game_state)
        
        # 3. 综合计算风险值
        risk_value = card_probability * opponent_hu_probability * self._get_card_value_risk(card)
        
        return risk_value
    
    def _calculate_card_probability(self, card: 'Card', game_state: 'GameState') -> float:
        """计算某张牌在剩余牌中的概率"""
        # 实现概率计算逻辑
        total_remaining = len(game_state.deck)
        if total_remaining == 0:
            return 0.0
            
        # 统计已经出现的该牌数量
        appeared_count = 0
        for p in game_state.players:
            appeared_count += sum(1 for c in p.hand if c == card)
            appeared_count += sum(1 for meld in p.melds for c in meld if c == card)
        
        for c in game_state.discard_pile:
            if c == card:
                appeared_count += 1
        
        remaining_count = 4 - appeared_count
        return remaining_count / total_remaining
    
    def _estimate_opponent_hu_probability(self, player: 'Player', game_state: 'GameState') -> float:
        """评估对手听牌的可能性"""
        # 实现对手听牌概率估计逻辑
        # 基于对手已经打出的牌、吃碰杠情况等进行估计
        probability = 0.0
        # 简化实现：根据牌局阶段估计概率
        total_tiles = self.rule.tiles_count
        remaining_tiles = len(game_state.deck)
        progress = (total_tiles - remaining_tiles) / total_tiles
        
        # 牌局越靠后，对手听牌概率越高
        probability = min(progress * 2, 1.0)
        
        return probability
    
    def _get_card_value_risk(self, card: 'Card') -> float:
        """获取牌的价值风险系数"""
        # 实现牌价值风险计算逻辑
        # 字牌的价值风险通常高于序数牌
        if card.suit in ['风', '箭']:
            return 1.5
        return 1.0
```

## 四、核心工作流程

### 1. 游戏初始化流程
```python
def init_game(rule_name: str, players_config: list) -> 'GameState':
    """初始化游戏
    
    Args:
        rule_name: 使用的规则名称
        players_config: 玩家配置列表
    
    Returns:
        初始化后的游戏状态
    """
    # 1. 创建游戏状态
    game_state = GameState(rule_name)
    
    # 2. 加载规则
    rule = load_rule(rule_name)
    game_state.rule = rule
    
    # 3. 创建玩家
    from src.core.data.player import Player
    for config in players_config:
        player = Player(config["name"], config["is_ai"])
        if config.get("ai_strategy"):
            player.ai_strategy = load_ai_strategy(config["ai_strategy"])
        game_state.players.append(player)
    
    # 4. 设置玩家位置和邻居关系
    positions = ['东', '南', '西', '北']
    for i, player in enumerate(game_state.players):
        player.position = positions[i]
        player.is_dealer = (i == 0)  # 第一个玩家为庄家
        player.previous_player = game_state.players[(i - 1) % len(game_state.players)]
        player.next_player = game_state.players[(i + 1) % len(game_state.players)]
    
    # 5. 洗牌和发牌
    from src.core.logic.deck_manager import shuffle_and_deal
    shuffle_and_deal(game_state)
    
    # 6. 设置游戏阶段为进行中
    game_state.current_player = game_state.players[0]  # 庄家先出牌
    game_state.game_stage = "playing"
    
    return game_state
```

### 2. 回合处理流程
```python
def process_turn(game_state: 'GameState') -> 'Action':
    """处理单个玩家的回合
    
    Returns:
        玩家执行的操作
    """
    current_player = game_state.current_player
    rule = game_state.rule
    
    # 1. 摸牌
    from src.core.logic.deck_manager import draw_card
    drawn_card = draw_card(game_state)
    current_player.drawn_card = drawn_card
    
    # 2. 检查是否可以自摸胡牌
    if rule.can_hu(current_player, drawn_card):
        action = Action("hu", drawn_card)
        from src.core.logic.turn_handler import execute_action
        execute_action(action, game_state)
        return action
    
    # 3. 获取有效操作列表
    valid_actions = rule.get_valid_actions(current_player, game_state)
    
    # 4. AI决策或玩家输入
    if current_player.is_ai:
        from src.ai.decision import AI_Decision
        ai_decision = AI_Decision(current_player.ai_strategy, rule)
        action = ai_decision.make_decision(current_player, game_state, valid_actions)
    else:
        from src.interface.game_api import get_player_input
        action = get_player_input(current_player, game_state, valid_actions)
    
    # 5. 执行操作
    from src.core.logic.turn_handler import execute_action
    execute_action(action, game_state)
    
    # 6. 检查是否有其他玩家可以胡牌（如果是打牌操作）
    if action.type == "discard" and rule.allow_other_hu:
        for player in game_state.players:
            if player != current_player and rule.can_hu(player, action.card):
                hu_action = Action("hu", action.card, current_player)
                execute_action(hu_action, game_state)
                return hu_action
    
    # 7. 切换到下一个玩家
    from src.core.logic.turn_handler import switch_player
    switch_player(game_state)
    
    return action
```

## 五、技术选型

| 模块 | 技术/框架 | 理由 |
|------|-----------|------|
| 编程语言 | Python 3.8+ | 开发效率高，适合快速原型开发；有丰富的数学计算和算法库；语法简洁，易于维护和扩展；可跨平台运行 |
| 核心逻辑 | 纯Python | 无需外部依赖，便于维护和部署 |
| 数学计算 | numpy | 高效的数值计算支持，适合概率计算和AI算法 |
| 随机数生成 | random模块 | 内置随机数生成器，满足游戏需求 |
| 日志管理 | logging模块 | 内置日志系统，配置灵活 |
| 测试框架 | pytest | 强大的测试框架，支持单元测试和集成测试 |
| 类型检查 | mypy | 静态类型检查，提高代码质量 |
| UI框架（可选） | Tkinter/PyQt | 跨平台GUI支持，便于开发可视化界面 |
| 性能优化 | Cython/numba | 关键算法的性能加速，提高AI决策速度 |

## 六、实现计划

### 第一阶段（2-3周）：核心框架搭建
1. 实现核心数据结构（Card, Player, GameState, Action）
2. 实现基础规则基类和框架
3. 实现腾讯大众麻将规则核心功能
4. 实现基本的游戏流程控制
5. 编写单元测试

### 第二阶段（2-3周）：AI决策系统开发
1. 实现基础AI策略
2. 实现危险牌预测模块
3. 实现手牌评估模块
4. 优化AI决策算法
5. 编写AI相关测试

### 第三阶段（1-2周）：功能完善和测试
1. 完善腾讯大众麻将规则的所有功能
2. 实现游戏控制接口
3. 编写集成测试
4. 修复bug和性能优化

### 第四阶段（可选，2-4周）：高级功能开发
1. 开发可视化界面
2. 支持多种规则切换
3. 实现AI难度分级
4. 添加统计分析功能

## 七、扩展性考虑

1. **规则扩展**：通过继承BaseRule类，可以轻松添加新的麻将规则
2. **AI策略扩展**：通过继承BaseStrategy类，可以添加新的AI策略
3. **界面扩展**：通过继承BaseUI类，可以添加新的用户界面
4. **功能扩展**：通过模块化设计，可以方便地添加新功能，如联网对战、回放等

## 八、重点难点分析

### 1. 规则系统设计
- **挑战**：不同麻将规则差异很大，需要一个灵活的规则框架
- **解决方案**：采用抽象基类+具体实现的方式，每种规则独立实现；将规则分解为胡牌规则、操作规则、计分规则等子模块

### 2. 胡牌判定算法
- **挑战**：需要高效判断各种复杂牌型的胡牌条件
- **解决方案**：实现基于动态规划的通用胡牌判定算法，支持基本牌型和特殊牌型

### 3. 危险牌预测
- **挑战**：需要准确评估打出某张牌的风险
- **解决方案**：结合概率计算、对手行为分析和牌型价值评估，采用分层评估策略

### 4. AI决策系统
- **挑战**：麻将是不完全信息博弈，需要考虑多种因素
- **解决方案**：采用分层决策架构，从简单到复杂逐步优化；结合规则引擎和机器学习算法

## 九、测试策略

1. **单元测试**：测试每个核心类和方法的功能，使用pytest进行测试
2. **规则测试**：针对每种规则的核心功能进行测试，确保规则的正确性
3. **AI测试**：测试AI决策的合理性和性能，使用模拟对局进行测试
4. **集成测试**：测试整个游戏流程的完整性，确保各模块协同工作正常
5. **性能测试**：测试AI决策的速度和资源占用，优化关键算法

## 十、部署和运行

### 运行方式
```bash
# 终端运行
python main.py --rule tencent_common --players ai,ai,ai,ai

# 使用配置文件运行
python main.py --config config/tencent_common.json
```

### 配置文件示例
```json
{
  "rule_name": "tencent_common",
  "players": [
    {"name": "AI1", "is_ai": true, "ai_strategy": "simple"},
    {"name": "AI2", "is_ai": true, "ai_strategy": "advanced"},
    {"name": "AI3", "is_ai": true, "ai_strategy": "simple"},
    {"name": "AI4", "is_ai": true, "ai_strategy": "advanced"}
  ],
  "log_level": "INFO",
  "output_format": "text"
}
```

## 十一、总结

本架构设计采用了模块化、可扩展的设计理念，将麻将游戏的核心功能分解为多个独立模块，便于维护和扩展。重点实现了规则系统的灵活性，支持多种麻将规则的扩展；AI决策系统采用分层设计，支持不同水平的AI策略；危险牌预测模块结合多种因素进行风险评估，提高AI的决策质量。

通过清晰的目录结构和接口设计，确保了代码的可读性和可维护性，便于后续功能的扩展和优化。