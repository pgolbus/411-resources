from typing import Any

from wildlife_tracker.migration_tracking.migration_path import MigrationPath

class Migration:

    def __init__(self, migration_id: int, migration_path: MigrationPath, start_date: str, current_location: str, status: str = "Scheduled"):
        self.migration_id = migration_id
        self.migration_path = migration_path
        self.start_date = start_date
        self.current_location = current_location
        self.status = status

    def get_migration_details(self) -> dict[str, Any]:
        return {
            "migration_id": self.migration_id,
            "migration_path": self.migration_path.path_id,
            "start_date": self.start_date,
            "current_location": self.current_location,
            "status": self.status
        }

    def update_migration_details(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)