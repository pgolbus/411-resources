import pytest
import logging
from unittest.mock import patch

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

@pytest.fixture
def sample_meal1():
    """Fixture providing a sample meal for testing."""
    return Meal(1, "Pizza", "Italian", 15.99, "MED")

@pytest.fixture
def sample_meal2():
    """Fixture providing another sample meal for testing."""
    return Meal(2, "Burger", "American", 12.99, "LOW")

@pytest.fixture
def sample_meal3():
    """Fixture providing a third sample meal for testing."""
    return Meal(3, "Sushi", "Japanese", 18.99, "HIGH")

##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant(battle_model, sample_meal1):
    """Test preparing a single combatant for battle."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Pizza"

def test_prep_combatant_full_list(battle_model, sample_meal1, sample_meal2, sample_meal3):
    """Test error when preparing too many combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(sample_meal3)

def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing all combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0

def test_clear_combatants_empty_list(battle_model, caplog):
    """Test clearing combatants when list is already empty."""
    caplog.set_level(logging.INFO)
    battle_model.clear_combatants()
    assert "Clearing the combatants list" in caplog.text

##################################################
# Battle Score Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test battle score calculation."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = (15.99 * len("Italian")) - 2  # MED difficulty modifier is 2
    assert score == pytest.approx(expected_score, 0.01)

def test_get_battle_score_different_difficulties(battle_model, sample_meal1, sample_meal2, sample_meal3):
    """Test battle score calculation with different difficulties."""
    score1 = battle_model.get_battle_score(sample_meal1)  # MED
    score2 = battle_model.get_battle_score(sample_meal2)  # LOW
    score3 = battle_model.get_battle_score(sample_meal3)  # HIGH
    
    assert score2 < score1 < score3

##################################################
# Battle Execution Test Cases
##################################################

def test_battle_execution(battle_model, sample_meal1, sample_meal2, mock_get_random, mock_update_meal_stats):
    """Test full battle execution with predetermined random value."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    mock_get_random.return_value = 0.05
    winner = battle_model.battle()
    
    assert winner == "Pizza"
    mock_update_meal_stats.assert_any_call(1, 'win')
    mock_update_meal_stats.assert_any_call(2, 'loss')

def test_battle_insufficient_combatants(battle_model, sample_meal1):
    """Test error when battling with insufficient combatants."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped"):
        battle_model.battle()

def test_battle_removes_loser(battle_model, sample_meal1, sample_meal2, mock_update_meal_stats):
    """Test that losing combatant is removed after battle."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    with patch('meal_max.models.battle_model.get_random', return_value=0.05):
        battle_model.battle()
    
    assert len(battle_model.combatants) == 1
    assert battle_model.combatants[0].meal == "Pizza"

##################################################
# Logging Test Cases
##################################################

def test_battle_logging(battle_model, sample_meal1, sample_meal2, caplog, mock_update_meal_stats):
    """Test battle event logging."""
    caplog.set_level(logging.INFO)
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    with patch('meal_max.models.battle_model.get_random', return_value=0.05):
        battle_model.battle()
    
    assert "Two meals enter, one meal leaves!" in caplog.text
    assert "Battle started between Pizza and Burger" in caplog.text

def test_prep_combatant_logging(battle_model, sample_meal1, caplog):
    """Test combatant preparation logging."""
    caplog.set_level(logging.INFO)
    battle_model.prep_combatant(sample_meal1)
    assert "Adding combatant 'Pizza' to combatants list" in caplog.text

def test_clear_combatants_logging(battle_model, sample_meal1, caplog):
    """Test combatant clearing logging."""
    caplog.set_level(logging.INFO)
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert "Clearing the combatants list" in caplog.text
