from dataclasses import asdict
import pytest
from boxer.models.boxer_model import BoxerModel
from boxer.models.boxer import Boxer


@pytest.fixture()
def boxer_model():
    """Fixture to provide a new instance of BoxerModel for each test."""
    return BoxerModel()


@pytest.fixture
def mock_update_boxer_stats(mocker):
    """Mock the update_boxer_stats function for testing purposes."""
    return mocker.patch("boxer.models.boxer_model.update_boxer_stats")


@pytest.fixture()
def sample_boxer1():
    return Boxer(1, 'Boxer 1', 'Heavyweight', 25, 10, 5)


@pytest.fixture()
def sample_boxer2():
    return Boxer(2, 'Boxer 2', 'Middleweight', 30, 15, 3)


@pytest.fixture()
def sample_boxers(sample_boxer1, sample_boxer2):
    return [sample_boxer1, sample_boxer2]


##################################################
# Add / Remove Boxer Management Test Cases
##################################################


def test_add_boxer_to_team(boxer_model, sample_boxer1):
    """Test adding a boxer to the team."""
    boxer_model.add_boxer_to_team(sample_boxer1)
    assert len(boxer_model.team) == 1
    assert boxer_model.team[0].name == 'Boxer 1'


def test_add_duplicate_boxer_to_team(boxer_model, sample_boxer1):
    """Test error when adding a duplicate boxer to the team by ID."""
    boxer_model.add_boxer_to_team(sample_boxer1)
    with pytest.raises(ValueError, match="Boxer with ID 1 already exists in the team"):
        boxer_model.add_boxer_to_team(sample_boxer1)


def test_add_bad_boxer_to_team(boxer_model, sample_boxer1):
    """Test error when adding a bad boxer (not an instance of Boxer)."""
    with pytest.raises(TypeError, match="Boxer is not a valid Boxer instance"):
        boxer_model.add_boxer_to_team(asdict(sample_boxer1))


def test_remove_boxer_from_team_when_empty(boxer_model):
    """Test removing a boxer from an empty team."""
    with pytest.raises(ValueError, match="Team is empty, cannot remove boxer"):
        boxer_model.remove_boxer_by_boxer_id(1)


def test_remove_boxer_from_team_by_boxer_id(boxer_model, sample_boxers):
    """Test removing a boxer from the team by boxer_id."""
    boxer_model.team.extend(sample_boxers)
    assert len(boxer_model.team) == 2

    boxer_model.remove_boxer_by_boxer_id(1)
    assert len(boxer_model.team) == 1
    assert boxer_model.team[0].id == 2


def test_remove_boxer_by_name(boxer_model, sample_boxers):
    """Test removing a boxer from the team by name."""
    boxer_model.team.extend(sample_boxers)
    assert len(boxer_model.team) == 2

    boxer_model.remove_boxer_by_name('Boxer 1')
    assert len(boxer_model.team) == 1
    assert boxer_model.team[0].id == 2


def test_clear_team(boxer_model, sample_boxer1):
    """Test clearing the entire team."""
    boxer_model.team.append(sample_boxer1)

    boxer_model.clear_team()
    assert len(boxer_model.team) == 0, "Team should be empty after clearing"


##################################################
# Boxer Retrieval Test Cases
##################################################


def test_get_boxer_by_name(boxer_model, sample_boxers):
    """Test successfully retrieving a boxer from the team by name."""
    boxer_model.team.extend(sample_boxers)

    retrieved_boxer = boxer_model.get_boxer_by_name('Boxer 1')
    assert retrieved_boxer.id == 1
    assert retrieved_boxer.name == 'Boxer 1'
    assert retrieved_boxer.weight_class == 'Heavyweight'


def test_get_all_boxers(boxer_model, sample_boxers):
    """Test successfully retrieving all boxers from the team."""
    boxer_model.team.extend(sample_boxers)

    all_boxers = boxer_model.get_all_boxers()
    assert len(all_boxers) == 2
    assert all_boxers[0].id == 1
    assert all_boxers[1].id == 2


def test_get_boxer_by_boxer_id(boxer_model, sample_boxer1):
    """Test successfully retrieving a boxer from the team by boxer ID."""
    boxer_model.team.append(sample_boxer1)

    retrieved_boxer = boxer_model.get_boxer_by_boxer_id(1)

    assert retrieved_boxer.id == 1
    assert retrieved_boxer.name == 'Boxer 1'
    assert retrieved_boxer.weight_class == 'Heavyweight'


def test_get_team_size(boxer_model, sample_boxers):
    """Test getting the size of the team."""
    boxer_model.team.extend(sample_boxers)
    assert boxer_model.get_team_size() == 2, "Expected team size to be 2"


##################################################
# Boxer Statistics Test Cases
##################################################


def test_update_boxer_stats(boxer_model, sample_boxer1, mock_update_boxer_stats):
    """Test updating boxer statistics."""
    boxer_model.add_boxer_to_team(sample_boxer1)

    boxer_model.update_boxer_stats(1, wins=1, losses=0, draws=0)

    mock_update_boxer_stats.assert_called_once_with(1)
    assert sample_boxer1.wins == 11, "Expected 11 wins"
    assert sample_boxer1.losses == 5, "Expected 5 losses"
    assert sample_boxer1.draws == 5, "Expected 5 draws"


def test_get_boxer_stats(boxer_model, sample_boxer1):
    """Test retrieving a boxer's statistics."""
    boxer_model.add_boxer_to_team(sample_boxer1)

    stats = boxer_model.get_boxer_stats(1)

    assert stats['wins'] == 10
    assert stats['losses'] == 5
    assert stats['draws'] == 5


##################################################
# Helper Function Test Cases (for validation and checking emptiness)
##################################################


def test_check_if_empty_non_empty_team(boxer_model, sample_boxer1):
    """Test check_if_empty does not raise error if team is not empty."""
    boxer_model.team.append(sample_boxer1)
    try:
        boxer_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty team")


def test_check_if_empty_empty_team(boxer_model):
    """Test check_if_empty raises error when team is empty."""
    boxer_model.clear_team()
    with pytest.raises(ValueError, match="Team is empty"):
        boxer_model.check_if_empty()


def test_validate_boxer_id_valid(boxer_model, sample_boxer1):
    """Test validate_boxer_id does not raise error for valid boxer ID."""
    boxer_model.team.append(sample_boxer1)
    try:
        boxer_model.validate_boxer_id(1)
    except ValueError:
        pytest.fail("validate_boxer_id raised ValueError unexpectedly for valid boxer ID")


def test_validate_boxer_id_invalid_id(boxer_model):
    """Test validate_boxer_id raises error for invalid boxer ID."""
    with pytest.raises(ValueError, match="Invalid boxer id: -1"):
        boxer_model.validate_boxer_id(-1)

    with pytest.raises(ValueError, match="Invalid boxer id: invalid"):
        boxer_model.validate_boxer_id("invalid")


def test_validate_boxer_id_not_in_team(boxer_model, sample_boxer1):
    """Test validate_boxer_id raises error for boxer ID not in the team."""
    boxer_model.team.append(sample_boxer1)
    with pytest.raises(ValueError, match="Boxer with id 2 not found in team"):
        boxer_model.validate_boxer_id(2)


def test_validate_boxer_name_valid(boxer_model, sample_boxer1):
    """Test validate_boxer_name does not raise error for valid boxer name."""
    boxer_model.team.append(sample_boxer1)
    try:
        boxer_model.validate_boxer_name('Boxer 1')
    except ValueError:
        pytest.fail("validate_boxer_name raised ValueError unexpectedly for valid boxer name")


def test_validate_boxer_name_invalid(boxer_model):
    """Test validate_boxer_name raises error for invalid boxer name."""
    with pytest.raises(ValueError, match="Invalid boxer name: invalid_name"):
        boxer_model.validate_boxer_name("invalid_name")


def test_validate_boxer_id_empty_team(boxer_model):
    """Test validate_boxer_id raises error when team is empty."""
    boxer_model.clear_team()
    with pytest.raises(ValueError, match="Team is empty, cannot validate boxer ID"):
        boxer_model.validate_boxer_id(1)