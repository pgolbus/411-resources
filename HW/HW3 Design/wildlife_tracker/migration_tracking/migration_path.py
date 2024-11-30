from typing import Optional, Any

from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:

    def __init__(self, path_id: int, species: str, start_location: Habitat, destination: Habitat, duration: Optional[int] = None):
        self.path_id = path_id
        self.species = species
        self.start_location = start_location
        self.destination = destination
        self.duration = duration

    def get_migration_path_details(self) -> dict:
        return {
            "path_id": self.path_id,
            "species": self.species,
            "start_location": self.start_location.habitat_id,
            "destination": self.destination.habitat_id,
            "duration": self.duration
        }

    def update_migration_path_details(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)