from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:
    def __init__(self, species: str, start_location: Habitat, end_location: Habitat, duration: int):
        self.species = species  
        self.start_location = start_location  
        self.end_location = end_location  
        self.duration = duration  

    def update_path_details(self, species: Optional[str] = None, start_location: Optional[Habitat] = None, end_location: Optional[Habitat] = None, duration: Optional[int] = None) -> None:
        if species:
            self.species = species
        if start_location:
            self.start_location = start_location
        if end_location:
            self.end_location = end_location
        if duration:
            self.duration = duration
        print("Migration path details updated.")
