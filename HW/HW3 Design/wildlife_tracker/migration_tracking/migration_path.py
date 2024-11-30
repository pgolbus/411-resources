from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:
    def __init__(self, path_id: int, destination: Habitat, species: str,start_location: Habitat, duration: Optional[int]):
        self.path_id = path_id
        self.destination = Habitat 
        self.species = species
        self.start_location = Habitat
        self.duration = Optional[int]

def update_migration_path_details(path_id: int, **kwargs) -> None:
    pass

def get_migration_path_details(path_id) -> dict: 
    pass

