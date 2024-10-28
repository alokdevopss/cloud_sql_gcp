#!/bin/bash

# Source Database Configuration
SRC_HOST="localhost"
SRC_DB="sample_db"
SRC_USER="root"
SRC_DUMP_DIR="src_backup"

# Source Database Configuration
TRG_HOST="localhost"
TRG_DB="restore_db"
TRG_USER="root"
TRG_DUMP_DIR="trg_backup"

################################### Data dump ######################################################

echo "*********************** TAKING DUMP EACH TABLE's IN SOURCE DATABASE ***********************"
# Ensure backup directory exists
mkdir -p "$SRC_DUMP_DIR"

#databases=$(mysql  -u $SRC_USER -h $SRC_HOST -e "show databases;")
tables=$(mysql -u $SRC_USER -h $SRC_HOST -D $SRC_DB -sN -e "SHOW TABLES;")

#echo "Databases are in MySQL are:-" $databases
#echo "Tables are in sample_db are:-" $tables

for table in ${tables[@]}; do
        # Dump each table
        mysqldump -u $SRC_USER -h $SRC_HOST $SRC_DB $table > $SRC_DUMP_DIR/$table.sql
        echo "Successfully backup done for table:  " $table
done

echo "Data successfully saved in $SRC_DUMP_DIR."
echo " "

################################### Data restore ######################################################

# Ensure destination database backup directory exists
mkdir -p "$TRG_DUMP_DIR"

echo "*********************** LISTING TABLE's IN DESTINATION DATABASE ***********************"

# Iterate over each dump file in the directory
tables_in_restore_db=$(mysql -u $TRG_USER -h $TRG_HOST -D $TRG_DB -sN -e "SHOW TABLES;")
echo "tables_in_$TRG_DB: "$tables
echo " "

# Iterate through each dump file in the source directory
for dump_file in "$SRC_DUMP_DIR"/*.sql; do
    table_name=$(basename "$dump_file" .sql)

    echo "Table_name_which_has_to_be_restore========>>>>>>>>>> $table_name"

    # Check if the table is in the list of tables to be processed
    if echo "$tables_in_restore_db" | grep -wq "$table_name"; then
        echo "$table_name========>>>>>>>>>> found in the list."

        # Check if the table exists in the database
        if mysql -u "$TRG_USER" -h "$TRG_HOST" -e "USE $TRG_DB; SHOW TABLES LIKE '$table_name';" | grep -q "$table_name"; then
            echo "Table $table_name exists in the database."

            # Backup existing table
            echo "Backing up========>>>>>>>>>> $table_name..."
            mysqldump -u "$TRG_USER" -h "$TRG_HOST" "$TRG_DB" "$table_name" > "$TRG_DUMP_DIR/${table_name}_backup.sql"

            # Drop existing table
            echo "Dropping========>>>>>>>>>> $table_name..."
            mysql -u "$TRG_USER" -h "$TRG_HOST" -e "USE $TRG_DB; DROP TABLE IF EXISTS $table_name;"
        else
            echo "Table $table_name does not exist in the database."
        fi
    else
        echo "$table_name not found in the list of tables to be processed."
    fi

    # Restore the dump file to the database
    echo "Restoring $table_name from $dump_file..."
    mysql -u "$TRG_USER" -h "$TRG_HOST" "$TRG_DB" < "$dump_file"

    #echo "$table_name restored successfully."
    echo "*********************** $table_name restored successfully. ***********************"
    echo " "
done
echo "Data successfully transferred to the target database."

# Clean up the temporary file
#rm -rf "$SRC_DUMP_DIR"
#echo "Deleted dump directory."