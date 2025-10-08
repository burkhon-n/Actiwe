#!/usr/bin/env python3
"""
Automatic Database Migration System
Compares SQLAlchemy models with actual database schema and adds missing columns.
"""

import logging
from typing import Dict, List, Set, Tuple, Any
from sqlalchemy import inspect, text, Column
from sqlalchemy.sql.sqltypes import TypeEngine
from database import engine, Base
from models import User, Admin, Item, Order, CartItem, ShopTheme

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """Handles automatic database migrations by comparing models with actual schema."""
    
    def __init__(self):
        self.engine = engine
        self.inspector = inspect(engine)
        self.models = [User, Admin, Item, Order, CartItem, ShopTheme]
        
    def get_model_columns(self, model_class) -> Dict[str, Dict[str, Any]]:
        """Extract column information from SQLAlchemy model."""
        columns = {}
        
        for column_name, column in model_class.__table__.columns.items():
            # Get column type as string
            column_type = str(column.type)
            
            # Handle special cases for PostgreSQL types
            if hasattr(column.type, 'python_type'):
                if column.type.python_type == bool:
                    column_type = "BOOLEAN"
                elif hasattr(column.type, 'enums') and column.type.enums:
                    # Handle enum types
                    enum_name = getattr(column.type, 'name', column_name)
                    column_type = f"USER-DEFINED"  # PostgreSQL enum type
            
            columns[column_name] = {
                'type': column_type,
                'nullable': column.nullable,
                'default': column.default,
                'primary_key': column.primary_key,
                'autoincrement': getattr(column, 'autoincrement', False),
                'unique': column.unique,
                'foreign_key': len(column.foreign_keys) > 0
            }
        
        return columns
    
    def get_database_columns(self, table_name: str) -> Dict[str, Dict[str, Any]]:
        """Get actual column information from database."""
        columns = {}
        
        try:
            # Get column information from database
            db_columns = self.inspector.get_columns(table_name)
            
            for col in db_columns:
                column_type = str(col['type'])
                
                columns[col['name']] = {
                    'type': column_type,
                    'nullable': col['nullable'],
                    'default': col.get('default'),
                    'primary_key': col.get('primary_key', False),
                    'autoincrement': col.get('autoincrement', False),
                    'unique': False,  # Will be checked separately if needed
                    'foreign_key': False  # Will be checked separately if needed
                }
            
        except Exception as e:
            logger.warning(f"Could not get columns for table {table_name}: {e}")
            
        return columns
    
    def get_missing_columns(self, model_class) -> List[Tuple[str, Dict[str, Any]]]:
        """Find columns that exist in model but not in database."""
        table_name = model_class.__tablename__
        model_columns = self.get_model_columns(model_class)
        db_columns = self.get_database_columns(table_name)
        
        missing = []
        for col_name, col_info in model_columns.items():
            if col_name not in db_columns:
                missing.append((col_name, col_info))
        
        return missing
    
    def get_sqlalchemy_type_to_sql(self, column_info: Dict[str, Any]) -> str:
        """Convert SQLAlchemy column type to SQL DDL type."""
        col_type = column_info['type']
        
        # Map common SQLAlchemy types to PostgreSQL types
        type_mapping = {
            'INTEGER': 'INTEGER',
            'BIGINT': 'BIGINT',
            'VARCHAR': 'VARCHAR',
            'TEXT': 'TEXT',
            'BOOLEAN': 'BOOLEAN',
            'TIMESTAMP': 'TIMESTAMP',
            'DATETIME': 'TIMESTAMP',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'FLOAT': 'FLOAT',
            'DECIMAL': 'DECIMAL',
            'NUMERIC': 'NUMERIC',
            'UUID': 'UUID',
            'JSON': 'JSON',
            'JSONB': 'JSONB'
        }
        
        # Handle VARCHAR with length
        if 'VARCHAR(' in col_type:
            return col_type
        
        # Handle basic type mapping
        for sqlalchemy_type, sql_type in type_mapping.items():
            if sqlalchemy_type in col_type.upper():
                return sql_type
        
        # Default fallback
        if col_type == 'USER-DEFINED':
            return col_type  # Will be handled as enum
        
        return 'TEXT'  # Safe fallback
    
    def create_enum_if_needed(self, model_class, column_name: str) -> str:
        """Create enum type if needed and return the enum name."""
        column = getattr(model_class.__table__.columns, column_name, None)
        if not column:
            return None
            
        if hasattr(column.type, 'enums') and column.type.enums:
            enum_name = getattr(column.type, 'name', f"{model_class.__tablename__}_{column_name}")
            enum_values = column.type.enums
            
            # Create enum type using separate connection without transactions
            try:
                # Use raw connection without transaction for DDL
                raw_conn = self.engine.raw_connection()
                cursor = raw_conn.cursor()
                
                try:
                    # Check if enum already exists
                    cursor.execute("SELECT 1 FROM pg_type WHERE typname = %s", (enum_name,))
                    
                    if not cursor.fetchone():
                        # Create enum type
                        enum_values_str = ', '.join([f"'{value}'" for value in enum_values])
                        cursor.execute(f"CREATE TYPE {enum_name} AS ENUM ({enum_values_str})")
                        raw_conn.commit()
                        logger.info(f"✅ Created enum type '{enum_name}'")
                    
                finally:
                    cursor.close()
                    raw_conn.close()
                
                return enum_name
                
            except Exception as e:
                logger.error(f"❌ Failed to create enum '{enum_name}': {e}")
                return None
        
        return None
    
    def add_missing_column(self, table_name: str, column_name: str, column_info: Dict[str, Any], model_class) -> bool:
        """Add a missing column to the database table."""
        try:
            # First, create enum type if needed (outside any transaction)
            enum_name = self.create_enum_if_needed(model_class, column_name)
            
            # Now add the column
            with self.engine.connect() as conn:
                trans = conn.begin()
                
                try:
                    if enum_name:
                        sql_type = enum_name
                    else:
                        sql_type = self.get_sqlalchemy_type_to_sql(column_info)
                    
                    # Build ALTER TABLE statement
                    alter_parts = []
                    alter_parts.append(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}")
                    
                    # Handle default values
                    if column_info['default'] is not None:
                        if hasattr(column_info['default'], 'arg'):
                            # Handle SQLAlchemy defaults
                            default_value = column_info['default'].arg
                            if isinstance(default_value, bool):
                                alter_parts.append(f"DEFAULT {str(default_value).lower()}")
                            elif isinstance(default_value, str):
                                alter_parts.append(f"DEFAULT '{default_value}'")
                            else:
                                alter_parts.append(f"DEFAULT {default_value}")
                        elif column_info['nullable']:
                            alter_parts.append("DEFAULT NULL")
                    
                    # Handle nullable constraint
                    if not column_info['nullable']:
                        alter_parts.append("NOT NULL")
                    
                    # Execute the ALTER TABLE command
                    alter_sql = " ".join(alter_parts)
                    conn.execute(text(alter_sql))
                    trans.commit()
                    
                    logger.info(f"✅ Added column '{column_name}' ({sql_type}) to table '{table_name}'")
                    return True
                    
                except Exception as e:
                    trans.rollback()
                    logger.error(f"❌ Failed to add column '{column_name}' to table '{table_name}': {e}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            return False
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if table exists in database."""
        return table_name in self.inspector.get_table_names()
    
    def create_missing_table(self, model_class) -> bool:
        """Create a completely missing table."""
        try:
            table_name = model_class.__tablename__
            logger.info(f"🔨 Creating missing table '{table_name}'...")
            
            # Create table using SQLAlchemy
            model_class.__table__.create(self.engine)
            logger.info(f"✅ Created table '{table_name}'")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create table '{model_class.__tablename__}': {e}")
            return False
    
    def migrate_model(self, model_class) -> Dict[str, Any]:
        """Migrate a single model."""
        table_name = model_class.__tablename__
        model_name = model_class.__name__
        
        logger.info(f"\n🔍 Checking model: {model_name} (table: {table_name})")
        
        result = {
            'model': model_name,
            'table': table_name,
            'table_existed': True,
            'columns_added': [],
            'errors': []
        }
        
        # Check if table exists
        if not self.check_table_exists(table_name):
            logger.warning(f"⚠️  Table '{table_name}' does not exist")
            result['table_existed'] = False
            
            if self.create_missing_table(model_class):
                result['table_created'] = True
                logger.info(f"✅ Table '{table_name}' created successfully")
            else:
                result['errors'].append(f"Failed to create table '{table_name}'")
                return result
        
        # Special handling for Admin model broadcasting column
        if model_name == 'Admin' and table_name == 'admins':
            try:
                return self._handle_admin_broadcasting_migration(result, model_class)
            except Exception as e:
                logger.error(f"❌ Special Admin migration failed: {e}")
                result['errors'].append(f"Admin broadcasting migration failed: {e}")
                # Continue with normal migration process as fallback
                pass
        
        # Check for missing columns
        missing_columns = self.get_missing_columns(model_class)
        
        if not missing_columns:
            logger.info(f"✅ All columns exist for {model_name}")
            return result
        
        logger.info(f"📝 Found {len(missing_columns)} missing column(s) in {table_name}:")
        for col_name, col_info in missing_columns:
            logger.info(f"   - {col_name}: {col_info['type']}")
        
        # Add missing columns
        for col_name, col_info in missing_columns:
            if self.add_missing_column(table_name, col_name, col_info, model_class):
                result['columns_added'].append(col_name)
            else:
                result['errors'].append(f"Failed to add column '{col_name}'")
        
        return result
    
    def _handle_admin_broadcasting_migration(self, result, model_class) -> Dict[str, Any]:
        """Special handler for Admin model broadcasting column migration"""
        try:
            logger.info("📝 Found 1 missing column(s) in admins:")
            logger.info("   - broadcasting: USER-DEFINED")
            
            # Use a completely separate engine instance to avoid transaction conflicts
            from database import DATABASE_URL
            from sqlalchemy import create_engine
            temp_engine = create_engine(DATABASE_URL)
            
            with temp_engine.connect() as conn:
                # Check if broadcasting column exists (double-check)
                col_check = conn.execute(text("""
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'admins' AND column_name = 'broadcasting'
                """))
                
                if col_check.fetchone():
                    logger.info("✅ All columns exist for Admin")
                    temp_engine.dispose()
                    return result
                
                # Use autocommit for DDL operations
                conn = conn.execution_options(autocommit=True)
                
                try:
                    # Check and create enum if needed
                    enum_check = conn.execute(text("SELECT 1 FROM pg_type WHERE typname = 'broadcasting'"))
                    if not enum_check.fetchone():
                        conn.execute(text("CREATE TYPE broadcasting AS ENUM ('forward', 'copy')"))
                        logger.info("✅ Created broadcasting enum")
                    
                    # Add column
                    conn.execute(text("ALTER TABLE admins ADD COLUMN broadcasting broadcasting"))
                    
                    result['columns_added'].append('broadcasting')
                    logger.info("✅ Added column 'broadcasting' (broadcasting) to table 'admins'")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to add broadcasting column: {e}")
                    result['errors'].append(f"Failed to add column 'broadcasting'")
            
            temp_engine.dispose()
                
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            result['errors'].append(f"Database connection error: {e}")
            
        return result
    
    def run_migrations(self) -> Dict[str, Any]:
        """Run migrations for all models."""
        logger.info("🚀 Starting automatic database migration...")
        logger.info(f"📊 Checking {len(self.models)} models...")
        
        results = {
            'total_models': len(self.models),
            'models_processed': 0,
            'tables_created': 0,
            'columns_added': 0,
            'errors': [],
            'details': []
        }
        
        for model_class in self.models:
            try:
                model_result = self.migrate_model(model_class)
                results['details'].append(model_result)
                results['models_processed'] += 1
                
                if not model_result['table_existed']:
                    results['tables_created'] += 1
                
                results['columns_added'] += len(model_result['columns_added'])
                results['errors'].extend(model_result['errors'])
                
            except Exception as e:
                error_msg = f"Failed to migrate {model_class.__name__}: {e}"
                logger.error(f"❌ {error_msg}")
                results['errors'].append(error_msg)
        
        return results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print migration summary."""
        logger.info("\n" + "="*60)
        logger.info("� MIGRATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Models processed: {results['models_processed']}/{results['total_models']}")
        logger.info(f"Tables created: {results['tables_created']}")
        logger.info(f"Columns added: {results['columns_added']}")
        logger.info(f"Errors: {len(results['errors'])}")
        
        if results['errors']:
            logger.info("\n❌ ERRORS:")
            for error in results['errors']:
                logger.error(f"  - {error}")
        
        logger.info("\n📋 DETAILED RESULTS:")
        for detail in results['details']:
            status = "✅" if not detail['errors'] else "❌"
            logger.info(f"{status} {detail['model']}: {len(detail['columns_added'])} columns added")
            
            if detail['columns_added']:
                for col in detail['columns_added']:
                    logger.info(f"    + {col}")
        
        if results['columns_added'] > 0 or results['tables_created'] > 0:
            logger.info("\n🎉 Migration completed successfully!")
        else:
            logger.info("\n✅ Database is up to date!")

def run_migrations():
    """Main function to run migrations."""
    migrator = DatabaseMigrator()
    results = migrator.run_migrations()
    migrator.print_summary(results)
    return results

if __name__ == "__main__":
    run_migrations()