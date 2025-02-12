from typing import Optional, List

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.animal_management.animal import Animal

class HabitatManager:

    def __init__(self) -> None:
        self.habitats: dict[int, Habitat] = {}

    def register_habitat(self, habitat_id: int, geographic_area: str, size: int, environment_type: str) -> Habitat:
        if habitat_id not in self.habitats:
            habitat = Habitat(habitat_id, geographic_area, size, environment_type)
            self.habitats[habitat_id] = habitat
            print(f"Habitat {habitat_id} registered.")
            return habitat
        else:
            print(f"Habitat {habitat_id} already exists.")
            return self.habitats[habitat_id]

    def remove_habitat(self, habitat_id: int) -> None:
        if habitat_id in self.habitats:
            del self.habitats[habitat_id]
            print(f"Habitat {habitat_id} removed.")
        else:
            print(f"Habitat {habitat_id} not found.")

    def get_habitat_by_id(self, habitat_id: int) -> Optional[Habitat]:
        return self.habitats.get(habitat_id)

    def get_habitats_by_geographic_area(self, geographic_area: str) -> List[Habitat]:
        return [habitat for habitat in self.habitats.values() if habitat.geographic_area == geographic_area]

    def get_habitats_by_size(self, size: int) -> List[Habitat]:
        return [habitat for habitat in self.habitats.values() if habitat.size == size]

    def get_habitats_by_type(self, environment_type: str) -> List[Habitat]:
        return [habitat for habitat in self.habitats.values() if habitat.environment_type == environment_type]

    def assign_animals_to_habitat(self, habitat_id: int, animals: List[Animal]) -> None:
        habitat = self.get_habitat_by_id(habitat_id)
        if habitat:
            habitat.assign_animals_to_habitat(animals)
        else:
            print(f"Habitat with ID {habitat_id} not found.")

    def get_animals_in_habitat(self, habitat_id: int) -> Optional[List[Animal]]:
        habitat = self.get_habitat_by_id(habitat_id)
        if habitat:
            return habitat.get_animals_in_habitat()
        else:
            print(f"Habitat with ID {habitat_id} not found.")
            return None

    def get_habitat_details(self, habitat_id: int) -> Optional[dict]:
        habitat = self.get_habitat_by_id(habitat_id)
        if habitat:
            return habitat.get_habitat_details()
        else:
            print(f"Habitat with ID {habitat_id} not found.")
            return None

