#!/usr/bin/env python3
"""
演示如何使用重构后的GUI系统

这个脚本展示了：
1. 如何初始化不同规则的游戏
2. 如何使用规则页面渲染状态
3. 页面系统的核心概念
"""

def demonstrate_page_system():
    """演示页面系统的工作原理"""
    print("=" * 60)
    print("GUI 页面系统演示")
    print("=" * 60)
    
    # 1. 展示可用的规则和对应页面
    print("\n📋 可用的规则和页面：")
    print("  • tencent_common (腾讯大众) -> CommonPage")
    print("  • tencent_xueliu (血流成河) -> XueliuPage")
    
    # 2. 演示规则特性差异
    print("\n🎮 规则特性对比：")
    
    from src.core.logic.turn_handler import init_game
    
    players = [
        {"name": "玩家", "is_ai": False},
        {"name": "AI-1", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-2", "is_ai": True, "ai_strategy": "advanced"},
        {"name": "AI-3", "is_ai": True, "ai_strategy": "advanced"},
    ]
    
    # 腾讯大众
    print("\n  【腾讯大众麻将】")
    common_game = init_game("tencent_common", players)
    print(f"    - 牌数: {len(common_game.deck) + sum(len(p.hand) for p in common_game.players)} 张")
    print(f"    - 允许吃牌: {common_game.rule.allow_chow}")
    print(f"    - 允许碰杠: {common_game.rule.allow_pong}")
    print(f"    - 最大番数: {common_game.rule.max_fans}")
    print(f"    - 风牌: 有")
    print(f"    - 花牌: 有")
    
    # 血流成河
    print("\n  【血流成河麻将】")
    xueliu_game = init_game("tencent_xueliu", players)
    print(f"    - 牌数: {len(xueliu_game.deck) + sum(len(p.hand) for p in xueliu_game.players)} 张")
    print(f"    - 允许吃牌: {xueliu_game.rule.allow_chow}")
    print(f"    - 允许碰杠: {xueliu_game.rule.allow_pong}")
    print(f"    - 最大番数: {xueliu_game.rule.max_fans}")
    print(f"    - 定缺: 有 (每位玩家)")
    for p in xueliu_game.players:
        que = getattr(p, "que_men", "未定")
        print(f"      {p.name}: 缺 {que}")
    print(f"    - 多胡: 支持一炮多响")
    
    # 3. 展示页面接口
    print("\n🎨 RulePage 接口方法：")
    print("  • setup_ui(parent) - 初始化UI组件")
    print("  • render_state(game_state) - 刷新游戏状态显示")
    print("  • render_actions(player, game_state, valid_actions, callback) - 渲染动作按钮")
    print("  • render_hand(player, callback) - 渲染手牌按钮")
    print("  • reset() - 重置页面状态")
    print("  • get_widget() - 获取顶层widget")
    
    # 4. 展示如何添加新规则
    print("\n➕ 添加新规则的步骤：")
    print("  1. 在 src/rules/ 下实现规则逻辑")
    print("  2. 创建 src/ui/your_rule_page.py 实现 RulePage")
    print("  3. 在 mahjong_ui.py 中注册到 rule_pages 字典")
    print("  4. 在 rule_selector 下拉框中添加选项")
    
    # 5. 展示动作流程
    print("\n🔄 人类玩家动作流程：")
    print("  1. MainWindow._tick() 检测到人类玩家回合")
    print("  2. 调用 _render_player_ui() 委托给规则页面")
    print("  3. 页面调用 render_hand() 和 render_actions()")
    print("  4. 用户点击按钮触发 action_callback")
    print("  5. callback 调用 MainWindow.handle_player_action()")
    print("  6. 执行动作并更新游戏状态")
    print("  7. 回到步骤 1")
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("\n💡 提示：")
    print("  • 查看 UI_REFACTOR_GUIDE.md 获取详细文档")
    print("  • 运行 python src/ui/mahjong_ui.py 启动GUI")
    print("  • 运行 python test_ui_refactor.py 验证系统")


if __name__ == "__main__":
    demonstrate_page_system()
