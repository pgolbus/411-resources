from typing import Optional

from wildlife_tracker.animal_managment.animal import Animal

class AnimalManager:

    def __init__(self) -> None:
        self.animals: dict[int, Animal] = {}

    def get_animal_by_id(self, animal_id: int) -> Optional[Animal]:
        return self.animals.get(animal_id, None)

    def register_animal(self, Animal) -> None:
        if Animal.animal_id not in self.animals:
            self.animals[Animal.animal_id] = Animal
            print(f"Animal with ID {Animal.animal_id} registered.")
        else:
            print(f"Animal with ID {Animal.animal_id} already exists.")

    def remove_animal(self, animal_id: int) -> None:
        if animal_id in self.animals:
            del self.animals[animal_id]
            print(f"Animal with ID {animal_id} removed.")
        else:
            print(f"Animal with ID {animal_id} not found.")
