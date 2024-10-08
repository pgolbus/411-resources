from typing import Any
from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_tracking.migration_path import MigrationPath

class Migration:
    def __init__(self, migration_id: int, migration_path: MigrationPath, start_date: str, status: str = "Scheduled") -> None:
        self.migration_id = migration_id
        self.migration_path = migration_path
        self.start_date = start_date
        self.status = status

    def get_migration_details(self) -> dict[str, Any]:
        """Return a dictionary of migration details."""
        return {
            "migration_id": self.migration_id,
            "path_id": self.migration_path.path_id,
            "start_date": self.start_date,
            "status": self.status,
            "species": self.migration_path.species,
            "start_location": self.migration_path.start_location.habitat_id,
            "destination": self.migration_path.destination.habitat_id,
            "duration": self.migration_path.duration,
        }