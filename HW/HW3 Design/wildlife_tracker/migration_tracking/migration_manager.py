from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.animal_management.animal import Animal


class MigrationManager:
    def __init__(self) -> None:
        migrations: dict[int, Migration] = {}
        paths: dict[int, MigrationPath] = {} # make sure of both lists should be here

def get_migration_by_id(migration_id: int) -> Migration:
    pass

def get_migration_path_by_id(path_id: int) -> MigrationPath:
    pass

def get_migration_paths() -> list[MigrationPath]:
    pass

def get_migrations() -> list[Migration]:
    pass

def get_migration_paths_by_destination(destination: Habitat) -> list[MigrationPath]:
    pass

def get_migration_paths_by_species(species: str) -> list[MigrationPath]:
    pass

def get_migration_paths_by_start_location(start_location: Habitat) -> list[MigrationPath]:
    pass

def get_migrations_by_current_location(current_location: str) -> list[Migration]:
    pass

def get_migrations_by_migration_path(migration_path_id: int) -> list[Migration]:
    pass

def get_migrations_by_start_date(start_date: str) -> list[Migration]:
    pass

def get_migrations_by_status(status: str) -> list[Migration]:
    pass

def remove_migration_path(path_id: int) -> None:
    pass

def schedule_migration(migration_path: MigrationPath) -> None:
    pass


