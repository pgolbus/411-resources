from typing import Optional, List

from wildlife_tracker.habitat_management.habitat import Habitat

class HabitatManager:

    def __init__(self):
        self.habitats: dict[int, Habitat] = {}

    def create_habitat(self, habitat_id: int, geographic_area: str, size: int, environment_type: str) -> Habitat:
        habitat = Habitat(habitat_id, geographic_area, size, environment_type)
        self.habitats[habitat_id] = habitat
        return habitat

    def remove_habitat(self, habitat_id: int) -> None:
        if habitat_id in self.habitats:
            del self.habitats[habitat_id]

    def get_habitat_by_id(self, habitat_id: int) -> Optional[Habitat]:
        return self.habitats.get(habitat_id)

    def get_habitat_details(self, habitat_id: int) -> dict:
        habitat = self.get_habitat_by_id(habitat_id)
        return habitat.get_habitat_details() if habitat else {}

    def update_habitat_details(self, habitat_id: int, **kwargs: dict[str, Any]) -> None:
        habitat = self.get_habitat_by_id(habitat_id)
        if habitat:
            habitat.update_habitat_details(**kwargs)

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

    def get_animals_in_habitat(self, habitat_id: int) -> List[Animal]:
        habitat = self.get_habitat_by_id(habitat_id)
        return habitat.get_animals_in_habitat() if habitat else []

    
