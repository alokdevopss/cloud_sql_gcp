#!/bin/bash

# Source Database Configuration
SRC_HOST="localhost"
SRC_PORT="5432"
SRC_DB="postgres"
SRC_USER="postgres"
SRC_PASSWORD="password"
OUTPUT_DIR="db"

# Target Database Configuration
TRG_HOST="localhost"
TRG_PORT="5432"
TRG_DB="mydb"
TRG_USER="postgres"
TRG_PASSWORD="password"

################################### Data dump ######################################################

# Ensure backup directory exists
mkdir -p "$OUTPUT_DIR"

# Export PostgreSQL password environment variables for non-interactive connection
export PGPASSWORD=$SRC_PASSWORD

# List of tables to dump
tables=('employees13' 'employees10')

# Check if there are tables to dump
if [ ${#tables[@]} -eq 0 ]; then
    echo "No tables specified for dumping."
    exit 1
fi

# Dump each table
for table in "${tables[@]}"; do
    # Filter today's entries and save to a CSV file
    PGPASSWORD="$SRC_PASSWORD" psql -h "$SRC_HOST" -p "$SRC_PORT" -U "$SRC_USER" -d "$SRC_DB" -c \
    "COPY (SELECT * FROM $table WHERE DATE(created_at) = CURRENT_DATE) TO STDOUT WITH CSV HEADER;" \
    > "$OUTPUT_DIR/$table.dump"

    echo "Filtered today's entries for $table into $OUTPUT_DIR/$table.dump."
done

echo "Data successfully saved in $OUTPUT_DIR."
ls "$OUTPUT_DIR"

################################### Data restore ######################################################

# Export PostgreSQL password environment variables for non-interactive connection
export PGPASSWORD=$TRG_PASSWORD

# Iterate over each dump file in the directory
for dump_file in "$OUTPUT_DIR"/*; do
    table_name=$(basename "$dump_file" .dump)

    echo "Restoring $table_name from $dump_file..."

    # Restore the dump file to the database
    PGPASSWORD="$TRG_PASSWORD" psql -h "$TRG_HOST" -p "$TRG_PORT" -U "$TRG_USER" -d "$TRG_DB" -c \
    "\copy $table_name FROM '$dump_file' WITH CSV HEADER"

    echo "$table_name restored successfully."
done

echo "Data successfully transferred to the target database."

# Clean up the temporary file
rm -rf "$OUTPUT_DIR"
echo "Deleted dump directory."