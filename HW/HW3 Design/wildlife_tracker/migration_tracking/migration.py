from typing import Any
from migration_path import MigrationPath

class Migration:

    def __init__(self, 
                 migration_id: int,
                 migration_path: MigrationPath) -> None:
        pass

    def get_migration_details(migration_id: int) -> dict[str, Any]:
        pass

    def update_migration_details(migration_id: int, **kwargs: Any) -> None:
        pass