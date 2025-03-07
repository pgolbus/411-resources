from dataclasses import asdict

import pytest

from meal_max.models.kitchen_model import Meals

@pytest.fixture
def mock_redis_client(mocker):
    return mocker.patch('meal_max.models.kitchen_model.redis_client')

######################################################
#
#    Add and delete
#
######################################################

def test_add_meal(session):
    """Test adding a meal to the database."""
    meal = Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")

    # Query back the meal to check it was added
    result = Meals.query.one()
    assert result.meal == "Spaghetti"
    assert result.cuisine == "Italian"
    assert result.price == 12.5
    assert result.difficulty == "MED"

def test_add_meal_invalid_price():
    """Test error when trying to create a meal with an invalid price (negative or zero)."""
    with pytest.raises(ValueError, match="Invalid price: -12.5. Price must be a positive number."):
        Meals.create_meal("Spaghetti", "Italian", -12.5, "MED")

    with pytest.raises(ValueError, match="Invalid price: 0. Price must be a positive number."):
        Meals.create_meal("Spaghetti", "Italian", 0, "MED")

def test_add_meal_invalid_difficulty():
    """Test error when trying to create a meal with an invalid difficulty level."""
    with pytest.raises(ValueError, match="Invalid difficulty level: VERY_HARD. Must be 'LOW', 'MED', or 'HIGH'."):
        Meals.create_meal("Spaghetti", "Italian", 12.5, "VERY_HARD")

def test_add_meal_duplicate_name(session):
    """Test adding a meal with a duplicate name."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    with pytest.raises(ValueError, match="Meal with name 'Spaghetti' already exists"):
        # Attempt to create a duplicate meal
        Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
        session.rollback()  # Rollback the transaction to clean up

def test_delete_meal(session, mock_redis_client):
    """Test soft deleting a meal by marking it as deleted."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.delete_meal(meal.id)

    # Fetch the meal to confirm it's marked as deleted
    result = session.get(Meals, 1)
    assert result.deleted is True

def test_delete_meal_triggers_cache_delete(session, mock_redis_client):
    """Test that deleting a meal triggers cache removal in Redis."""
    # Create and add a meal
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = session.get(Meals, 1)

    # Delete the meal
    Meals.delete_meal(meal.id)

    # Check that the Redis cache entry was deleted
    mock_redis_client.delete.assert_called_once_with(f"meal:{meal.id}")

def test_delete_meal_bad_id(session):
    """Test deleting a meal that does not exist."""
    with pytest.raises(ValueError, match="Meal 999 not found"):
        Meals.delete_meal(999)

def test_get_meal_by_id_cache_hit(session, mock_redis_client):
    """Test retrieving a meal by its ID from cache."""
    # Create and add a meal to the database
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()

    # Set up mock Redis client to simulate cache hit with encoded data
    mock_redis_client.hgetall.return_value = {
        "id".encode(): "1".encode(),
        "meal".encode(): "Spaghetti".encode(),
        "cuisine".encode(): "Italian".encode(),
        "price".encode(): "12.5".encode(),
        "difficulty".encode(): "MED".encode(),
        "battles".encode(): "0".encode(),
        "wins".encode(): "0".encode(),
        "deleted".encode(): "False".encode(),
    }

    # Call the method
    result = Meals.get_meal_by_id(meal.id)

    # Assert Redis cache was accessed and the result is correct
    mock_redis_client.hgetall.assert_called_once_with(f"meal_1")
    assert result["meal"] == "Spaghetti"


def test_get_meal_by_id_cache_miss(session, mock_redis_client):
    """Test retrieving a meal by its ID when it is not in cache."""
    # Create and add a meal to the database
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()

    # Simulate cache miss by setting return_value to an empty dictionary
    mock_redis_client.hgetall.return_value = {}

    # Call the method
    result = Meals.get_meal_by_id(meal.id)

    # Assert Redis cache was accessed and data was subsequently cached with hset
    mock_redis_client.hgetall.assert_called_once_with(f"meal_{meal.id}")
    mock_redis_client.hset.assert_called_once_with(
        f"meal_1",
        mapping={
            "id": "1",
            "meal": "Spaghetti",
            "cuisine": "Italian",
            "price": "12.5",
            "difficulty": "MED",
            "battles": "0",
            "wins": "0",
            "deleted": "False",
        }
    )
    assert result["meal"] == "Spaghetti"

def test_get_meal_by_id_bad_id(session, mock_redis_client):
    """Test retrieving a meal by an invalid ID."""

    # Ensure the Redis client returns an empty dict to simulate a cache miss
    mock_redis_client.hgetall.return_value = {}

    with pytest.raises(ValueError, match="Meal 999 not found"):
        Meals.get_meal_by_id(999)

def test_get_meal_by_id_deleted(session, mock_redis_client):
    """Test retrieving a meal that has been marked as deleted."""

    # Set up the Redis client to return a deleted meal entry
    mock_redis_client.hgetall.return_value = {
        "id".encode(): "1".encode(),
        "meal".encode(): "Spaghetti".encode(),
        "cuisine".encode(): "Italian".encode(),
        "price".encode(): "12.5".encode(),
        "difficulty".encode(): "MED".encode(),
        "battles".encode(): "10".encode(),
        "wins".encode(): "5".encode(),
        "deleted".encode(): "True".encode(),  # Simulate the meal being marked as deleted
    }

    with pytest.raises(ValueError, match="Meal 1 not found"):
        Meals.get_meal_by_id(1)

def test_get_meal_by_name_cache_hit(session, mock_redis_client):
    """Test retrieving a meal by its name when the name-to-ID association is cached."""
    # Create the meal and cache the name-to-ID association
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    mock_redis_client.get.return_value = str(meal.id).encode()  # Simulate name-to-ID cache hit
    mock_redis_client.hgetall.return_value = {k.encode(): str(v).encode() for k, v in asdict(meal).items()}

    # Retrieve meal by name, expecting a cache hit for both ID and meal data
    result = Meals.get_meal_by_name("Spaghetti")
    mock_redis_client.get.assert_called_once_with("meal_name:Spaghetti")
    mock_redis_client.hgetall.assert_called_once_with(f"meal_{meal.id}")
    assert result["meal"] == "Spaghetti"

def test_get_meal_by_name_cache_miss(session, mock_redis_client):
    """Test retrieving a meal by its name when the name-to-ID association is not cached."""
    # Create the meal but simulate a cache miss for name-to-ID association
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    mock_redis_client.get.return_value = None  # Simulate cache miss for name-to-ID
    mock_redis_client.hgetall.return_value = {}  # Simulate cache miss for meal data

    # Retrieve meal by name; expect DB lookup and caching of both ID and meal data
    result = Meals.get_meal_by_name("Spaghetti")
    mock_redis_client.get.assert_called_once_with("meal_name:Spaghetti")
    mock_redis_client.set.assert_called_once_with("meal_name:Spaghetti", str(meal.id))
    mock_redis_client.hset.assert_called_once_with(f"meal_{meal.id}", mapping={k: str(v) for k, v in asdict(meal).items()})
    assert result["meal"] == "Spaghetti"

def test_get_meal_by_name_deleted(session, mock_redis_client):
    """Test retrieving a deleted meal by its name."""
    # Create and delete the meal
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.delete_meal(meal.id)

    # Cache reflects that the meal is deleted
    mock_redis_client.get.return_value = str(meal.id).encode()
    mock_redis_client.hgetall.return_value = {
        "id".encode(): "1".encode(),
        "meal".encode(): "Spaghetti".encode(),
        "cuisine".encode(): "Italian".encode(),
        "price".encode(): "12.5".encode(),
        "difficulty".encode(): "MED".encode(),
        "battles".encode(): "0".encode(),
        "wins".encode(): "0".encode(),
        "deleted".encode(): "True".encode()
    }

    # Attempt retrieval, expecting a ValueError
    with pytest.raises(ValueError, match="Meal Spaghetti not found"):
        Meals.get_meal_by_name("Spaghetti")

def test_get_meal_by_name_bad_name(session, mock_redis_client):
    """Test retrieving a meal by a name that does not exist in cache or database."""
    # Simulate a cache miss for a non-existent meal name
    mock_redis_client.get.return_value = None

    # Attempt retrieval, expecting a ValueError
    with pytest.raises(ValueError, match="Meal Motor oil not found"):
        Meals.get_meal_by_name("Motor oil")
    mock_redis_client.get.assert_called_once_with("meal_name:Motor oil")

def test_update_meal(session, mock_redis_client):
    """Test updating a meal's details."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.update_meal(meal.id, cuisine="Italian", price=15.0, difficulty="HIGH")
    updated_meal = Meals.query.one()
    assert updated_meal.cuisine == "Italian"
    assert updated_meal.price == 15.0
    assert updated_meal.difficulty == "HIGH"

def test_update_meal_triggers_cache_update(session, mock_redis_client):
    """Test that updating a meal triggers a cache update in Redis."""
    # Create and add a meal
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = session.get(Meals, 1)

    # Update the meal
    Meals.update_meal(meal.id, cuisine="Mexican", price=15.0)

    # Check that the Redis cache was updated with the new values
    mock_redis_client.hset.assert_called_once_with(
        f"meal:{meal.id}",
        mapping={
            b"id": b"1",
            b"meal": b"Spaghetti",
            b"cuisine": b"Mexican",
            b"price": b"15.0",
            b"difficulty": b"MED",
            b"battles": b"0",
            b"wins": b"0",
            b"deleted": b"False",
        }
    )

def test_update_meal_deleted(session, mock_redis_client):
    """Test updating a deleted meal."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.delete_meal(meal.id)
    with pytest.raises(ValueError, match="Meal 1 not found"):
        Meals.update_meal(meal.id, cuisine="Italian", price=15.0, difficulty="HIGH")

def test_update_meal_update_name(session):
    """Test updating a meal's name."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    with pytest.raises(ValueError, match="Cannot update meal name"):
        Meals.update_meal(meal.id, meal="Lasagna", cuisine="Italian", price=15.0, difficulty="HIGH")

def test_update_meal_bad_id(session):
    """Test updating a meal with an invalid ID."""
    with pytest.raises(ValueError, match="Meal 999 not found"):
        Meals.update_meal(999, cuisine="Italian", price=15.0, difficulty="HIGH")

def test_update_meal_bad_difficulty(session):
    """Test updating a meal with an invalid difficulty level."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    with pytest.raises(ValueError, match="Invalid difficulty level: VERY_HARD. Must be 'LOW', 'MED', or 'HIGH'."):
        Meals.update_meal(meal.id, cuisine="Italian", price=15.0, difficulty="VERY_HARD")

def test_update_meal_bad_price(session):
    """Test updating a meal with an invalid price (negative or zero)."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    with pytest.raises(ValueError, match="Invalid price: -15.0. Price must be a positive number."):
        Meals.update_meal(meal.id, cuisine="Italian", price=-15.0, difficulty="HIGH")

    session.rollback()

    with pytest.raises(ValueError, match="Invalid price: 0. Price must be a positive number."):
        Meals.update_meal(meal.id, cuisine="Italian", price=0, difficulty="HIGH")

def test_update_meal_stats_win(session, mock_redis_client):
    """Test updating the meal stats for a win."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.update_meal_stats(meal.id, 'win')
    updated_meal = Meals.query.one()
    assert updated_meal.wins == 1
    assert updated_meal.battles == 1

def test_update_meal_stats_loss(session, mock_redis_client):
    """Test updating the meal stats for a loss."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED")
    meal = Meals.query.one()
    Meals.update_meal_stats(meal.id, 'loss')
    updated_meal = Meals.query.one()
    assert updated_meal.wins == 0
    assert updated_meal.battles == 1

def test_get_leaderboard(session):
    """Test retrieving the leaderboard sorted by wins."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED", battles=10, wins=7)
    Meals.create_meal("Pizza", "Italian", 15.0, "LOW", battles=8, wins=5)

    leaderboard = Meals.get_leaderboard()
    assert leaderboard[0]["meal"] == "Spaghetti"
    assert leaderboard[1]["meal"] == "Pizza"

def test_get_leaderboard_sort_pct(session):
    """Test retrieving the leaderboard sorted by win percentage."""
    Meals.create_meal("Spaghetti", "Italian", 12.5, "MED", battles=10, wins=7)
    Meals.create_meal("Pizza", "Italian", 15.0, "LOW", battles=8, wins=5)

    leaderboard = Meals.get_leaderboard(sort_by="win_pct")
    assert leaderboard[0]["meal"] == "Spaghetti"
    assert leaderboard[1]["meal"] == "Pizza"

def test_get_leaderboard_bad_sort():
    """Test retrieving the leaderboard with an invalid sort option."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid_sort"):
        Meals.get_leaderboard(sort_by="invalid_sort")
