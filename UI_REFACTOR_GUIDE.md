# GUI 页面重构说明

## 概述

GUI 已重构为模块化的规则页面系统，支持为不同麻将规则定制独立的UI界面。

## 架构

### 核心组件

1. **RulePage 接口** (`src/ui/rule_page.py`)
   - 定义所有规则页面必须实现的方法
   - 方法包括：`setup_ui`, `render_state`, `render_actions`, `render_hand`, `reset`, `get_widget`

2. **规则专用页面**
   - **XueliuPage** (`src/ui/xueliu_page.py`) - 血流成河规则
     - 显示定缺信息
     - 缺门牌标红提示
     - 动作按钮：碰、杠、胡（无吃）
   
   - **CommonPage** (`src/ui/common_page.py`) - 腾讯大众规则
     - 显示场风、门风、花牌
     - 动作按钮：吃、碰、杠、胡、补花

3. **主窗口** (`src/ui/mahjong_ui.py`)
   - 规则选择下拉框
   - 动态切换规则页面
   - 管理游戏循环和状态更新

## 如何添加新规则的UI页面

### 步骤 1: 创建规则页面类

创建新文件 `src/ui/your_rule_page.py`:

```python
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from src.ui.rule_page import RulePage


class YourRulePage(RulePage):
    """你的规则专用UI页面"""

    def __init__(self):
        super().__init__()
        self._widget = None
        # ... 初始化其他组件

    def setup_ui(self, parent: QWidget):
        """初始化UI组件"""
        self._widget = QWidget(parent)
        layout = QVBoxLayout(self._widget)
        
        # 添加你的UI组件
        # ...
        
        return self._widget

    def render_state(self, game_state):
        """根据游戏状态刷新显示"""
        # 更新状态显示
        pass

    def render_actions(self, player, game_state, valid_actions: list, action_callback):
        """构建动作按钮"""
        # 创建动作按钮，调用 action_callback(action_type, card)
        pass

    def render_hand(self, player, action_callback):
        """渲染玩家手牌"""
        # 创建手牌按钮，调用 action_callback("discard", card)
        pass

    def reset(self):
        """重置页面状态"""
        pass

    def get_widget(self) -> QWidget:
        """返回页面的顶层widget"""
        return self._widget
```

### 步骤 2: 注册到主窗口

在 `src/ui/mahjong_ui.py` 中：

1. 导入你的页面类：
```python
from src.ui.your_rule_page import YourRulePage
```

2. 在 `rule_selector` 中添加规则选项：
```python
self.rule_selector.addItems(["tencent_common", "tencent_xueliu", "your_rule"])
```

3. 在 `rule_pages` 字典中注册：
```python
self.rule_pages = {
    "tencent_common": CommonPage(),
    "tencent_xueliu": XueliuPage(),
    "your_rule": YourRulePage(),  # 添加这一行
}
```

### 步骤 3: 实现规则逻辑

确保在 `src/rules/` 下有对应的规则实现，并在 `src/core/logic/turn_handler.py` 的 `init_game` 函数中添加规则映射。

## 运行GUI

```bash
python src/ui/mahjong_ui.py
```

或使用主入口：

```bash
python main.py  # 如果main.py已配置为启动PyQt UI
```

## 特性

- **动态规则切换**：通过下拉框选择不同规则，点击"开始游戏"立即切换
- **规则专用界面**：每个规则有独立的UI布局和控件
- **动作按钮定制**：不同规则展示不同的可用动作（如血流无吃，大众有吃）
- **手牌可视化**：按花色排序，特殊牌（缺门、花牌）自动高亮
- **实时状态更新**：分数、定缺、风位等信息实时显示

## 设计原则

1. **关注点分离**：规则逻辑与UI展示分离
2. **可扩展性**：添加新规则只需实现 `RulePage` 接口
3. **复用性**：主窗口逻辑复用，规则页面独立
4. **一致性**：所有规则页面遵循相同的接口约定

## 测试

运行测试脚本验证重构：

```bash
python test_ui_refactor.py
```

该脚本验证：
- 页面正确实现接口
- 游戏状态初始化
- 规则特定功能（定缺、吃牌等）
