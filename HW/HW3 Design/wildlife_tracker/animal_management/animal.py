from typing import Any, Optional

class Animal:
    def __init__(self, animal_id: int, name: str, species: str, age: Optional[int] = None, health_status: Optional[str] = None):
        
        self.animal_id = animal_id  # Unique ID for the animal
        self.name = name  # Name of the animal
        self.species = species  # Species of the animal
        self.age = age  # Optional age of the animal
        self.health_status = health_status  # Optional health status of the animal

    def __repr__(self):
        return f"Animal(ID={self.animal_id}, Name={self.name}, Species={self.species}, Age={self.age}, Health Status={self.health_status})"

