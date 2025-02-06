from wildlife_tracker.animal_management.animal_manager import AnimalManager
from wildlife_tracker.habitat_management.habitat_manger import HabitatManager
from wildlife_tracker.migration_tracking.migration_manager import MigrationManager

class WildlifeTracker:
    def __init__(self):
        self.animal_manager = AnimalManager()
        self.habitat_manager = HabitatManager()
        self.migration_manager = MigrationManager()