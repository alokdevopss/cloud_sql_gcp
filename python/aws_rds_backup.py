import os
import subprocess
from datetime import datetime

# Source Database Configuration
SRC_HOST = "localhost"
SRC_PORT = "5432"
SRC_DB = "postgres"
SRC_USER = "postgres"
SRC_PASSWORD = "password"
OUTPUT_DIR = "db"

# Target Database Configuration
TRG_HOST = "localhost"
TRG_PORT = "5432"
TRG_DB = "mydb"
TRG_USER = "postgres"
TRG_PASSWORD = "password"

# Names of the tables to dump
tables = ['employees1', 'employees4', 'employees5']

def execute_command(command):
    """Execute a shell command and return its output."""
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        raise Exception(f"Command failed with error: {result.stderr}")
    return result.stdout

def ensure_directory_exists(directory):
    """Ensure the output directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def dump_tables():
    """Dump today's entries from specified tables."""
    ensure_directory_exists(OUTPUT_DIR)
    os.environ['PGPASSWORD'] = SRC_PASSWORD

    for table in tables:
        query = f"COPY (SELECT * FROM {table} WHERE DATE(created_at) = CURRENT_DATE) TO STDOUT WITH CSV HEADER;"
        dump_file = os.path.join(OUTPUT_DIR, f"{table}.dump")
        command = f"psql -h {SRC_HOST} -p {SRC_PORT} -U {SRC_USER} -d {SRC_DB} -c \"{query}\" > {dump_file}"
        print(f"Filtering today's entries for {table} into {dump_file}.")
        execute_command(command)

def restore_tables():
    """Restore tables from dump files."""
    os.environ['PGPASSWORD'] = TRG_PASSWORD

    for dump_file in os.listdir(OUTPUT_DIR):
        table_name = os.path.splitext(dump_file)[0]
        dump_path = os.path.join(OUTPUT_DIR, dump_file)
        command = f"psql -h {TRG_HOST} -p {TRG_PORT} -U {TRG_USER} -d {TRG_DB} -c \"\\copy {table_name} FROM '{dump_path}' WITH CSV HEADER\""
        print(f"Restoring {table_name} from {dump_path}...")
        execute_command(command)
        print(f"{table_name} restored successfully.")

def main():
    """Main function to execute the dump and restore operations."""
    try:
        dump_tables()
        print(f"Data successfully saved in {OUTPUT_DIR}.")
        restore_tables()
        print("Data successfully transferred to the target database.")
    finally:
        # Clean up the temporary files
        if os.path.exists(OUTPUT_DIR):
            os.rmdir(OUTPUT_DIR)
            print(f"Deleted dump directory.")
        
if __name__ == "__main__":
    main()
