#!/bin/bash

# PostgreSQL connection details
PG_HOST="your_postgresql_host"
PG_PORT="5432"
PG_DATABASE="your_postgresql_database"
PG_USER="your_postgresql_user"
PG_PASSWORD="your_postgresql_password"

# MS SQL Server connection details
MSSQL_HOST="your_sql_server_host"
MSSQL_DATABASE="your_mssql_database"
MSSQL_USER="your_mssql_user"
MSSQL_PASSWORD="your_mssql_password"

# Export data from PostgreSQL
export PGPASSWORD="$PG_PASSWORD"
pg_dump -h $PG_HOST -p $PG_PORT -U $PG_USER -F c -b -v -f /tmp/postgresql_data.dump $PG_DATABASE

# Convert PostgreSQL dump to SQL format
pg_restore -d dummy_db_name -f /tmp/postgresql_data.sql /tmp/postgresql_data.dump

# Import data into MS SQL Server
sqlcmd -S $MSSQL_HOST -U $MSSQL_USER -P $MSSQL_PASSWORD -d $MSSQL_DATABASE -i /tmp/postgresql_data.sql

# Clean up
rm /tmp/postgresql_data.dump
rm /tmp/postgresql_data.sql

echo "Data transfer complete."
