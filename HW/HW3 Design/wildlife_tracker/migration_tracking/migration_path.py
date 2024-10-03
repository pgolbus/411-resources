from typing import Optional
from habitat_management.habitat import Habitat

class MigrationPath:
    
    def __init__(self, 
                 path_id: int,
                 size: int,
                 species: str,
                 start_date: str,
                 start_location: Habitat,
                 status: str = "Scheduled") -> None:
        
        self.path_id = path_id
        self.size = size
        self.species = species
        self.start_date = start_date
        self.start_location = start_location
        self.status = status

    def get_migration_path_details(path_id) -> dict:
        pass

    def update_migration_path_details(path_id: int, **kwargs) -> None:
        pass