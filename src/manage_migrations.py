#!/usr/bin/env python
# filepath: /workspaces/VoxaCommunications-Registry/src/manage_migrations.py
import argparse
import os
import sys
import dotenv
import time
from kvprocessor import KVStructLoader
from util.logging import log, set_log_config
from util.usefulJSON import JsonFromKeys
from lib.dbManager import DBManager
from lib.migrationManager import MigrationManager
from util.sqlExecutor import set_global_db_manager

# Load environment variables
dotenv.load_dotenv()

class MigrationCLI:
    def __init__(self):
        # Set up logging
        set_log_config(f"migration_{int(time.time())}")
        self.logger = log()
        self.logger.info("Migration CLI initialized")
        
        # Load configuration
        struct_loader_url = os.getenv(
            "STRUCT_LOADER_URL",
            "https://github.com/Voxa-Communications/VoxaCommunicaitons-Structures/raw/refs/heads/main/struct/config.json"
        )
        struct_loader = KVStructLoader(struct_loader_url)
        env_kv_processor = struct_loader.from_namespace("voxa.registry.config")
        
        # Connect to database
        db_config = JsonFromKeys(struct_loader.from_namespace("voxa.api.db.registrydb_config").return_names(), os.environ)
        self.db_manager = DBManager(db_config)
        set_global_db_manager(self.db_manager)
        
        # Initialize migration manager
        self.migration_manager = MigrationManager(self.db_manager)
    
    def create_migration(self, description):
        """Creates a new migration file."""
        try:
            filepath = self.migration_manager.create_migration(description)
            print(f"Created new migration: {filepath}")
            print("Edit this file to add your migration SQL commands.")
        except Exception as e:
            self.logger.error(f"Failed to create migration: {e}")
            print(f"Error: {e}")
            return 1
        return 0
    
    def apply_migrations(self):
        """Apply all pending migrations."""
        try:
            self.migration_manager.apply_migrations()
            print("All migrations applied successfully.")
        except Exception as e:
            self.logger.error(f"Failed to apply migrations: {e}")
            print(f"Error: {e}")
            return 1
        return 0
    
    def list_migrations(self):
        """List all applied and pending migrations."""
        try:
            applied = self.migration_manager.get_applied_migrations()
            all_files = self.migration_manager._get_migration_files()
            
            print("Applied migrations:")
            if not applied:
                print("  None")
            else:
                for m_id in applied:
                    print(f"  ✓ {m_id}")
            
            print("\nPending migrations:")
            pending = [f for f in all_files if self.migration_manager._get_migration_id_from_filename(f) not in applied]
            if not pending:
                print("  None")
            else:
                for p in pending:
                    m_id = self.migration_manager._get_migration_id_from_filename(p)
                    desc = self.migration_manager._get_migration_description(p)
                    print(f"  ⋯ {m_id}: {desc}")
        except Exception as e:
            self.logger.error(f"Failed to list migrations: {e}")
            print(f"Error: {e}")
            return 1
        return 0

def main():
    parser = argparse.ArgumentParser(description="Database migration tool for VoxaCommunications-Registry")
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create a new migration')
    create_parser.add_argument('description', help='Description of the migration')
    
    # Apply migrations command
    subparsers.add_parser('apply', help='Apply all pending migrations')
    
    # List migrations command
    subparsers.add_parser('list', help='List all migrations')
    
    args = parser.parse_args()
    
    cli = MigrationCLI()
    
    if args.command == 'create':
        return cli.create_migration(args.description)
    elif args.command == 'apply':
        return cli.apply_migrations()
    elif args.command == 'list':
        return cli.list_migrations()
    else:
        parser.print_help()
        return 0

if __name__ == '__main__':
    sys.exit(main())