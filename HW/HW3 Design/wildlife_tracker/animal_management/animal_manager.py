from typing import Optional
from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.animal_management.animal_manager import AnimalManager
from wildlife_tracker.habitat_management.habitat import habitat
from wildlife_tracker.migration_tracking.migration_manager import MigrationManager
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.migration_tracking.migration import Migration

class AnimalManager:

    def __init__(self) -> None:
        animals: dict[int, Animal] = {}

    def get_animal_by_id(self, animal_id: int) -> Optional[Animal]:
        pass

    def register_animal(self, Animal) -> None:
        pass

    def remove_animal(self, animal_id: int) -> None:
        pass

    
