from typing import Optional, Dict, Any

class Animal:

    def __init__(self, animal_id: int, species: str, age: Optional[int] = None, health_status: Optional[str] = None):
        self.animal_id = animal_id
        self.species = species
        self.age = age
        self.health_status = health_status

    def update_details(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "animal_id": self.animal_id,
            "species": self.species,
            "age": self.age,
            "health_status": self.health_status
        }
