#!/bin/bash

# source db postgres hai and dest ms sql hai

# PostgreSQL connection details
PG_HOST="your_postgresql_host"
PG_PORT="5432"
PG_DATABASE="your_postgresql_database"
PG_USER="your_postgresql_user"
PG_PASSWORD="your_postgresql_password"
OUTPUT_DIR="dump_dir"

# MS SQL Server connection details
MSSQL_HOST="your_sql_server_host"
MSSQL_PORT="1433"
MSSQL_DATABASE="your_mssql_database"
MSSQL_USER="your_mssql_user"
MSSQL_PASSWORD="your_mssql_password"

################################### Data dump ######################################################

# Ensure backup directory exists
mkdir -p "$OUTPUT_DIR"

# Export PostgreSQL password environment variables for non-interactive connection
export PGPASSWORD=$PG_PASSWORD

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
    PGPASSWORD="$PG_PASSWORD" psql -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -d "$PG_DATABASE" -c \
    "COPY (SELECT * FROM $table WHERE DATE(created_at) = CURRENT_DATE) TO STDOUT WITH CSV HEADER;" \
    > "$OUTPUT_DIR/$table.dump"

    # Convert PostgreSQL dump to SQL format
    pg_restore -d dummy_db_name -f /$OUTPUT_DIR/$table.sql /$OUTPUT_DIR/$table.dump

    # Import data into MS SQL Server
    sqlcmd -S $MSSQL_HOST -U $MSSQL_USER -P $MSSQL_PASSWORD -d $MSSQL_DATABASE -i /$OUTPUT_DIR/$table.sql

    echo "Filtered today's entries for $table into $OUTPUT_DIR/$table.dump."
    echo "$table_name restored successfully."
done

echo "Data successfully saved in $OUTPUT_DIR."
ls "$OUTPUT_DIR"

echo "Data successfully transferred to the target database."

# Clean up the temporary file
rm -rf "$OUTPUT_DIR"
echo "Deleted dump directory."

################################### Data restore ######################################################

# # Export PostgreSQL password environment variables for non-interactive connection
# export PGPASSWORD=$TRG_PASSWORD

# # Iterate over each dump file in the directory
# for dump_file in "$OUTPUT_DIR"/*; do
#     table_name=$(basename "$dump_file" .dump)

#     echo "Restoring $table_name from $dump_file..."

#     # Import data into MS SQL Server
#     sqlcmd -S $MSSQL_HOST -U $MSSQL_USER -P $MSSQL_PASSWORD -d $MSSQL_DATABASE -i /tmp/postgresql_data.sql

#     echo "$table_name restored successfully."
# done

# echo "Data successfully transferred to the target database."

# # Clean up the temporary file
# rm -rf "$OUTPUT_DIR"
# echo "Deleted dump directory."