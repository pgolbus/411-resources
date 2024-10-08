from typing import Optional, List
from wildlife_tracker.habitat_management.habitat import Habitat

class HabitatManager:

    def __init__(self) -> None:
        self.habitats: dict[int, Habitat] = {}

    def register_habitat(self, habitat: Habitat) -> None:
        """Registers a new habitat"""
        self.habitats[habitat.habitat_id] = habitat

    def update_habitat(self, habitat_id: int, **kwargs: dict) -> None:
        """Updates habitat details"""
        if habitat_id in self.habitats:
            habitat = self.habitats[habitat_id]
            habitat.geographic_area = kwargs.get('geographic_area', habitat.geographic_area)
            habitat.size = kwargs.get('size', habitat.size)
            habitat.environment_type = kwargs.get('environment_type', habitat.environment_type)
            habitat.animals = kwargs.get('animals', habitat.animals)  # Update animals if provided
        else:
            raise ValueError("Habitat ID not found.")

    def get_habitat_by_id(self, habitat_id: int) -> Optional[Habitat]:
        """Retrieves habitat by ID"""
        return self.habitats.get(habitat_id)

    def remove_habitat(self, habitat_id: int) -> None:
        """Removes habitat by ID"""
        if habitat_id in self.habitats:
            del self.habitats[habitat_id]
        else:
            raise ValueError("Habitat ID not found.")

    def get_all_habitats(self) -> List[Habitat]:
        """Returns a list of all habitats"""
        return list(self.habitats.values())