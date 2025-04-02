import pytest
from unittest.mock import MagicMock, patch

from boxing.models.ring_model import RingModel
from boxing.models.boxers_model import Boxer


class TestRingModel:
    """Tests for the RingModel class"""
    
    @pytest.fixture
    def ring_model(self):
        """Create a RingModel for testing"""
        return RingModel()
    
    @pytest.fixture
    def test_boxer_1(self):
        """Create a test boxer 1"""
        return Boxer(
            id=1,
            name="Mike Tyson",
            weight=220,
            height=178,
            reach=71.0,
            age=25
        )
    
    @pytest.fixture
    def test_boxer_2(self):
        """Create a test boxer 2"""
        return Boxer(
            id=2,
            name="Muhammad Ali",
            weight=210,
            height=191,
            reach=78.0,
            age=30
        )
    
    def test_init(self, ring_model):
        """Test initializing the RingModel class"""
        assert ring_model.ring == []
    
    def test_enter_ring(self, ring_model, test_boxer_1):
        """Test adding a boxer to the ring"""
        ring_model.enter_ring(test_boxer_1)
        assert len(ring_model.ring) == 1
        assert ring_model.ring[0].name == "Mike Tyson"
    
    def test_enter_ring_invalid_type(self, ring_model):
        """Test adding an invalid object to the ring"""
        with pytest.raises(TypeError):
            ring_model.enter_ring("Not a boxer")
    
    def test_enter_ring_full(self, ring_model, test_boxer_1, test_boxer_2):
        """Test adding more than 2 boxers to the ring"""
        ring_model.enter_ring(test_boxer_1)
        ring_model.enter_ring(test_boxer_2)
        
        with pytest.raises(ValueError, match="Ring is full"):
            ring_model.enter_ring(test_boxer_1)
    
    def test_clear_ring(self, ring_model, test_boxer_1):
        """Test clearing the ring"""
        ring_model.enter_ring(test_boxer_1)
        assert len(ring_model.ring) == 1
        
        ring_model.clear_ring()
        assert len(ring_model.ring) == 0
    
    def test_clear_empty_ring(self, ring_model):
        """Test clearing an empty ring"""
        # This should not raise an error
        ring_model.clear_ring()
        assert len(ring_model.ring) == 0
    
    def test_get_boxers(self, ring_model, test_boxer_1, test_boxer_2):
        """Test getting boxers from the ring"""
        ring_model.enter_ring(test_boxer_1)
        ring_model.enter_ring(test_boxer_2)
        
        boxers = ring_model.get_boxers()
        assert len(boxers) == 2
        assert boxers[0].name == "Mike Tyson"
        assert boxers[1].name == "Muhammad Ali"
    
    def test_get_fighting_skill(self, ring_model, test_boxer_1):
        """Test calculating a boxer's fighting skill"""
        # Calculate expected skill based on the formula in the method
        expected_skill = (test_boxer_1.weight * len(test_boxer_1.name)) + (test_boxer_1.reach / 10)
        # No age modifier since age is 25
        
        skill = ring_model.get_fighting_skill(test_boxer_1)
        assert skill == expected_skill
    
    def test_get_fighting_skill_with_age_modifier(self, ring_model):
        """Test fighting skill calculation with age modifiers"""
        # Test young boxer (age < 25)
        young_boxer = Boxer(id=3, name="Young", weight=180, height=175, reach=70, age=20)
        young_skill = ring_model.get_fighting_skill(young_boxer)
        expected_young = (young_boxer.weight * len(young_boxer.name)) + (young_boxer.reach / 10) - 1
        assert young_skill == expected_young
        
        # Test older boxer (age > 35)
        old_boxer = Boxer(id=4, name="Veteran", weight=190, height=182, reach=74, age=40)
        old_skill = ring_model.get_fighting_skill(old_boxer)
        expected_old = (old_boxer.weight * len(old_boxer.name)) + (old_boxer.reach / 10) - 2
        assert old_skill == expected_old
    
    @patch('boxing.models.ring_model.get_random')
    @patch('boxing.models.ring_model.update_boxer_stats')
    def test_fight_boxer1_wins(self, mock_update_stats, mock_random, ring_model, test_boxer_1, test_boxer_2):
        """Test fight simulation where boxer 1 wins"""
        # Make the random number small so boxer 1 wins (assuming skill_1 > skill_2)
        mock_random.return_value = 0.1
        
        ring_model.enter_ring(test_boxer_1)
        ring_model.enter_ring(test_boxer_2)
        
        winner_name = ring_model.fight()
        
        assert winner_name == test_boxer_1.name
        # Check if update_boxer_stats was called correctly
        mock_update_stats.assert_any_call(test_boxer_1.id, 'win')
        mock_update_stats.assert_any_call(test_boxer_2.id, 'loss')
        
        # Ring should be cleared after fight
        assert len(ring_model.ring) == 0
    
    @patch('boxing.models.ring_model.get_random')
    @patch('boxing.models.ring_model.update_boxer_stats')
    def test_fight_boxer2_wins(self, mock_update_stats, mock_random, ring_model, test_boxer_1, test_boxer_2):
        """Test fight simulation where boxer 2 wins"""
        # Make the random number large so boxer 2 wins
        mock_random.return_value = 0.9
        
        ring_model.enter_ring(test_boxer_1)
        ring_model.enter_ring(test_boxer_2)
        
        winner_name = ring_model.fight()
        
        assert winner_name == test_boxer_2.name
        # Check if update_boxer_stats was called correctly
        mock_update_stats.assert_any_call(test_boxer_2.id, 'win')
        mock_update_stats.assert_any_call(test_boxer_1.id, 'loss')
        
        # Ring should be cleared after fight
        assert len(ring_model.ring) == 0
    
    def test_fight_not_enough_boxers(self, ring_model, test_boxer_1):
        """Test trying to start a fight with less than 2 boxers"""
        ring_model.enter_ring(test_boxer_1)
        
        with pytest.raises(ValueError, match="There must be two boxers"):
            ring_model.fight() 