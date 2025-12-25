import pytest
from src.core.data.card import Card

def test_card_creation():
    """测试牌的创建"""
    card = Card("万", "1")
    assert card.suit == "万"
    assert card.rank == "1"
    assert card.id == "万1"
    assert not card.is_visible

def test_card_equality():
    """测试牌的相等性"""
    card1 = Card("万", "1")
    card2 = Card("万", "1")
    card3 = Card("万", "2")
    
    assert card1 == card2
    assert card1 != card3
    assert card1 != None

def test_card_repr():
    """测试牌的字符串表示"""
    card = Card("万", "1")
    assert repr(card) == "万1"
    
def test_card_hash():
    """测试牌的哈希值"""
    card1 = Card("万", "1")
    card2 = Card("万", "1")
    
    assert hash(card1) == hash(card2)
    
    # 测试牌可以作为字典的键
    card_dict = {}
    card_dict[card1] = "test"
    assert card_dict[card2] == "test"