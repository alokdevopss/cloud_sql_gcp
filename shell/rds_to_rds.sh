#!/bin/bash

# Source Database Configuration
SRC_HOST="source_db_host"
SRC_PORT="5432"
SRC_DB="source_db_name"
SRC_USER="source_db_user"
SRC_PASSWORD="source_db_password"

# Target Database Configuration
TGT_HOST="target_db_host"
TGT_PORT="5432"
TGT_DB="target_db_name"
TGT_USER="target_db_user"
TGT_PASSWORD="target_db_password"

# Export PostgreSQL password environment variables for non-interactive connection
export PGPASSWORD=$SRC_PASSWORD

# Get the current date in YYYY-MM-DD format
CURRENT_DATE=$(date +%Y-%m-%d)

# Formulate the SQL query using the current date
QUERY="SELECT * FROM table_name WHERE date_column = '$CURRENT_DATE';"

# Execute the query and save the output
psql -h $SRC_HOST -p $SRC_PORT -U $SRC_USER -d $SRC_DB -c "$QUERY" -F $'\t' --no-align --output /tmp/source_data.tsv

# Check if data was fetched successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to fetch data from source database."
    exit 1
fi

# Export target PostgreSQL password
export PGPASSWORD=$TGT_PASSWORD

# Insert data into the target database
while IFS=$'\t' read -r column1 column2 column3; do
    psql -h $TGT_HOST -p $TGT_PORT -U $TGT_USER -d $TGT_DB -c \
    "INSERT INTO your_table (column1, column2, column3) VALUES ('$column1', '$column2', '$column3');"
done < /tmp/source_data.tsv

# Check if the insert was successful
if [ $? -eq 0 ]; then
    echo "Data successfully transferred to the target database."
else
    echo "Error: Failed to insert data into the target database."
    exit 1
fi

# Clean up the temporary file
rm /tmp/source_data.tsv
