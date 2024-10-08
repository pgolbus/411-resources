from typing import Optional
from wildlife_tracker.habitat_management.habitat import Habitat
class MigrationPath:
    def __init__(self,
                 species: str,
                 start_location: Habitat,
                 destination: Habitat,
                 path_id: int,
                 duration: Optional[int] = None
                 ) -> None:
        self.destination = destination
        self.path_id = path_id
        self.species = species
        self.start_location = start_location
        self.duration = duration
    
    def get_migration_path_details(path_id) -> dict:
        pass

    def update_migration_path_details(path_id: int, **kwargs) -> None:
        pass
