import pytest
import logging

from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


@pytest.fixture()
def battle_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def mock_update_meal_stats(mocker):
    """Mock the update_meal_stats function for testing purposes."""
    return mocker.patch("meal_max.models.battle_model.update_meal_stats")

@pytest.fixture
def mock_get_random(mocker):
    """Mock the get_random function to return a predictable value."""
    return mocker.patch("meal_max.models.battle_model.get_random", return_value=0.5)

"""Fixtures providing sample meals for the tests."""
@pytest.fixture
def sample_meal1():
    return Meal(1, "Pizza", 15.99, "Italian", "MED")

@pytest.fixture
def sample_meal2():
    return Meal(2, "Burger", 12.99, "American", "LOW")


##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test adding a combatant to the battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Pizza"

def test_prep_combatant_full_list(battle_model, sample_meal1, sample_meal2):
    """Test error when adding a third combatant."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(sample_meal1)

def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing all combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test retrieving the list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Pizza"
    assert combatants[1].meal == "Burger"

##################################################
# Battle Score Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test battle score calculation."""
    score = battle_model.get_battle_score(sample_meal1)
    # Pizza: (15.99 * len("Italian")) - 2 (MED difficulty)
    expected_score = (15.99 * 7) - 2
    assert score == pytest.approx(expected_score, 0.01)

##################################################
# Battle Execution Test Cases
##################################################

def test_battle_insufficient_combatants(battle_model, sample_meal1):
    """Test error when starting battle with insufficient combatants."""
    battle_model.prep_combatant(sample_meal1)
    
    with pytest.raises(ValueError, match="Two combatants must be prepped"):
        battle_model.battle()

def test_battle_execution(battle_model, sample_meal1, sample_meal2, mock_get_random, mock_update_meal_stats):
    """Test full battle execution with predetermined random value."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    winner = battle_model.battle()
    
    # With mock_get_random returning 0.5, the higher battle score should win
    score1 = battle_model.get_battle_score(sample_meal1)
    score2 = battle_model.get_battle_score(sample_meal2)
    
    expected_winner = sample_meal1.meal if score1 > score2 else sample_meal2.meal
    assert winner == expected_winner
    
    # Verify stats were updated
    mock_update_meal_stats.assert_any_call(1, 'win' if winner == sample_meal1.meal else 'loss')
    mock_update_meal_stats.assert_any_call(2, 'win' if winner == sample_meal2.meal else 'loss')

def test_battle_removes_loser(battle_model, sample_meal1, sample_meal2):
    """Test that the losing combatant is removed after battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    battle_model.battle()
    
    assert len(battle_model.combatants) == 1, "Only winner should remain in combatants list"

def test_battle_logging(battle_model, sample_meal1, sample_meal2, caplog):
    """Test that battle events are properly logged."""
    caplog.set_level(logging.INFO)
    
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    battle_model.battle()
    
    assert "Two meals enter, one meal leaves!" in caplog.text
    assert f"Battle started between {sample_meal1.meal} and {sample_meal2.meal}" in caplog.text
    assert "The winner is:" in caplog.text
