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
        pass


    def get_migration_path_details(path_id) -> dict:
        pass
    
    def update_migration_path_details(path_id: int, **kwargs) -> None:
        pass