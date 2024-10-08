from typing import List, Optional
from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.habitat_management.habitat import Habitat

class Migration:
    def __init__(self, migration_id: int, animals: List[Animal], destination: Habitat, duration: Optional[int] = None, current_location: Optional[Habitat] = None):
        self.migration_id = migration_id  
        self.animals = animals  
        self.destination = destination  
        self.current_location = current_location  
        self.duration = duration  

    def update_details(self, destination: Optional[Habitat] = None, duration: Optional[int] = None) -> None:
        if destination:
            self.destination = destination
        if duration:
            self.duration = duration
        print(f"Migration {self.migration_id} details updated.")
