from typing import List, Optional
from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.animal_management.animal import Animal
from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationManager:
    def __init__(self) -> None:
        self.migrations: dict[int, Migration] = {}

    def register_migration(self, migration_id: int, animals: List[Animal], destination: Habitat, duration: Optional[int] = None) -> Migration:
        if migration_id not in self.migrations:
            migration = Migration(migration_id, animals, destination, duration)
            self.migrations[migration_id] = migration
            print(f"Migration {migration_id} registered.")
            return migration
        else:
            print(f"Migration {migration_id} already exists.")
            return self.migrations[migration_id]

    def remove_migration(self, migration_id: int) -> None:
        if migration_id in self.migrations:
            del self.migrations[migration_id]
            print(f"Migration {migration_id} removed.")
        else:
            print(f"Migration {migration_id} not found.")

    def get_migration_by_id(self, migration_id: int) -> Optional[Migration]:
        return self.migrations.get(migration_id)

    def retrieve_migrations(self) -> List[Migration]:
        return list(self.migrations.values())

    def update_migration(self, migration_id: int, destination: Optional[Habitat] = None, duration: Optional[int] = None) -> None:
        migration = self.get_migration_by_id(migration_id)
        if migration:
            migration.update_details(destination, duration)
        else:
            print(f"Migration with ID {migration_id} not found.")

    def schedule_migration(self, migration_id: int) -> None:
        if migration_id in self.migrations:
            print(f"Migration {migration_id} scheduled.")
        else:
            print(f"Migration with ID {migration_id} not found.")

    def cancel_migration(self, migration_id: int) -> None:
        if migration_id in self.migrations:
            print(f"Migration {migration_id} canceled.")
        else:
            print(f"Migration with ID {migration_id} not found.")

    def get_migrations_by_destination(self, destination: Habitat) -> List[Migration]:
        return [migration for migration in self.migrations.values() if migration.destination == destination]
