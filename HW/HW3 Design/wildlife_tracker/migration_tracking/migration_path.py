from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:
    def __init__(self,
                destination: Habitat,
                species: str = "",
                duration: Optional[int] = None,
                start_location: Habitat = [],
                path_id: int = 0) -> None:
        self.start_location = start_location
        self.path_id = path_id
        self.species = species
        self.destination = destination
        self.duration = duration
    def update_migration_path_details(path_id: int, **kwargs) -> None:
        pass

    def get_migration_path_details(path_id) -> dict:
        pass

    pass