Instances#!/bin/bash

# Variables
resourceGroup="test"
storageAccount="testdbscript"
containerName="test"
backupDirectory="/tmp/SQLBackups"
SASToken=" " # blob container SAS Token
server="localhost"  # MySQL server hostname or IP
username="root"     # MySQL username
password="password" # MySQL password

# Ensure backup directory exists
mkdir -p $backupDirectory

# Get the list of databases
databases=$(mysql -h $server -u $username -p$password -e 'SHOW DATABASES;' --silent --batch | grep -Ev '^(information_schema|mysql|performance_schema|sys)$')

# Backup databases and upload to Azure Blob Storage
for db in $databases; do
    if [ ! -z "$db" ]; then
        backupFile="$backupDirectory/$db.sql"

        # Backup database
        mysqldump -h $server -u $username -p$password $db > $backupFile

        # Upload to Azure Blob Storage
        az storage blob upload --account-name $storageAccount --container-name $containerName --name "$db/$(basename $backupFile)" --file $backupFile --sas-token $SASToken

        # Optional: Clean up local backup file
        rm $backupFile
    fi
done

echo "Backup completed and uploaded to Azure Blob Storage."
