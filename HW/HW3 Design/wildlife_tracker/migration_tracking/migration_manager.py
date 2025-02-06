from typing import Optional, List, Any

from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationManager:

    def __init__(self):
        self.migration_paths: dict[int, MigrationPath] = {}
        self.migrations: dict[int, Migration] = {}

    def create_migration_path(self, path_id: int, species: str, start_location: Habitat, destination: Habitat, duration: Optional[int] = None) -> MigrationPath:
        path = MigrationPath(path_id, species, start_location, destination, duration)
        self.migration_paths[path_id] = path
        return path

    def remove_migration_path(self, path_id: int) -> None:
        if path_id in self.migration_paths:
            del self.migration_paths[path_id]

    def get_migration_path_by_id(self, path_id: int) -> Optional[MigrationPath]:
        return self.migration_paths.get(path_id)

    def get_migration_paths(self) -> List[MigrationPath]:
        return list(self.migration_paths.values())

    def get_migration_paths_by_species(self, species: str) -> List[MigrationPath]:
        return [path for path in self.migration_paths.values() if path.species == species]

    def get_migration_paths_by_start_location(self, start_location: Habitat) -> List[MigrationPath]:
        return [path for path in self.migration_paths.values() if path.start_location == start_location]

    def get_migration_paths_by_destination(self, destination: Habitat) -> List[MigrationPath]:
        return [path for path in self.migration_paths.values() if path.destination == destination]

    def get_migration_path_details(self, path_id: int) -> dict:
        path = self.get_migration_path_by_id(path_id)
        return path.get_migration_path_details() if path else {}

    def update_migration_path_details(self, path_id: int, **kwargs) -> None:
        path = self.get_migration_path_by_id(path_id)
        if path:
            path.update_migration_path_details(**kwargs)

    def schedule_migration(self, migration_id: int, migration_path: MigrationPath, start_date: str, current_location: str) -> Migration:
        migration = Migration(migration_id, migration_path, start_date, current_location)
        self.migrations[migration_id] = migration
        return migration

    def cancel_migration(self, migration_id: int) -> None:
        if migration_id in self.migrations:
            self.migrations[migration_id].status = "Cancelled"

    def get_migration_by_id(self, migration_id: int) -> Optional[Migration]:
        return self.migrations.get(migration_id)

    def get_migrations(self) -> List[Migration]:
        return list(self.migrations.values())

    def get_migrations_by_current_location(self, current_location: str) -> List[Migration]:
        return [migration for migration in self.migrations.values() if migration.current_location == current_location]

    def get_migrations_by_migration_path(self, migration_path_id: int) -> List[Migration]:
        return [migration for migration in self.migrations.values() if migration.migration_path.path_id == migration_path_id]

    def get_migrations_by_start_date(self, start_date: str) -> List[Migration]:
        return [migration for migration in self.migrations.values() if migration.start_date == start_date]

    def get_migrations_by_status(self, status: str) -> List[Migration]:
        return [migration for migration in self.migrations.values() if migration.status == status]

    def get_migration_details(self, migration_id: int) -> dict[str, Any]:
        migration = self.get_migration_by_id(migration_id)
        return migration.get_migration_details() if migration else {}

    def update_migration_details(self, migration_id: int, **kwargs: Any) -> None:
        migration = self.get_migration_by_id(migration_id)
        if migration:
            migration.update_migration_details(**kwargs)
