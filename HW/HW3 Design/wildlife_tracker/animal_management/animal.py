from typing import Any, Optional

class Animal:
    def __init__(self,
                 animal_id: int,
                 age: Optional[int] = None) -> None:
        pass

    def get_animal_details(animal_id) -> dict[str, Any]:
        pass

    def update_animal_details(animal_id: int, **kwargs: Any) -> None:
        pass
    