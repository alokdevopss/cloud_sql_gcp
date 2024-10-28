USE MASTER

DECLARE @name NVARCHAR(50);
DECLARE @path NVARCHAR(256);
DECLARE @SASToken NVARCHAR(MAX);
DECLARE @fileName NVARCHAR(256);
DECLARE @fileDate NVARCHAR(20);
DECLARE @MaxFileSizeInGB INT = 50; -- 50GB in GB
DECLARE @BlobUrl NVARCHAR(MAX);
DECLARE @backupCommand NVARCHAR(4000);
DECLARE @retentionDays INT = 30; -- Retention period in days
DECLARE @timestamp NVARCHAR(20); -- Timestamp for unique file names

SET @path = 'https://bestdbbackup.blob.core.windows.net/best-buckups/supplydbserver/fullbackup/';
-- SET @path = 'https://testblob12345qwe.blob.core.windows.net/testsqlserver/';
SET @SASToken = ' ';
SET @fileDate = CONVERT(VARCHAR(20), GETDATE(), 112);

DECLARE db_cursor CURSOR FOR
SELECT name
FROM master.dbo.sysdatabases
WHERE name NOT IN ('master', 'model', 'msdb', 'tempdb', 'ReportServertempDB');

OPEN db_cursor;
FETCH NEXT FROM db_cursor INTO @name;

WHILE @@FETCH_STATUS = 0

BEGIN

    SET @timestamp = CONVERT(VARCHAR(20), GETDATE(), 120); -- Format: YYYY-MM-DD HH:MI:SS
    SET @timestamp = REPLACE(REPLACE(REPLACE(@timestamp, '-', ''), ':', ''), ' ', '_'); -- Remove separators
    SET @BlobUrl = @path + @name + '' + @fileDate + '' + @timestamp;

    -- Determine the database size in GB

    DECLARE @dbSizeInGB FLOAT;
    SELECT @dbSizeInGB = SUM(size) * 8.0 / 1024 / 1024
    FROM sys.master_files
    WHERE database_id = DB_ID(@name);

 
    IF @dbSizeInGB <= @MaxFileSizeInGB
    BEGIN
        SET @backupCommand = '
        BACKUP DATABASE [' + @name + ']
        TO URL = ''' + @BlobUrl + '.bak?' + @SASToken + ''' ' -- Include SAS token
        + 'WITH
            INIT,
            COMPRESSION,
            STATS = 2, -- Show progress every 2%
            CHECKSUM,
            FORMAT,
            MEDIANAME = ''AzureBlobBackup'',
            NAME = ''Full Backup of ' + @name + ''',
            SKIP,
            NOREWIND,
            NOUNLOAD,
            RETAINDAYS = ' + CAST(@retentionDays AS NVARCHAR);
    END
    ELSE
    BEGIN
        -- Backup to multiple files

        SET @backupCommand = '
        BACKUP DATABASE [' + @name + ']
        TO URL = ''' + @BlobUrl + '_Part1.bak?' + @SASToken + ''' ' -- Include SAS token
        + 'URL = ''' + @BlobUrl + '_Part2.bak?' + @SASToken + ''' ' -- Include SAS token
        + 'URL = ''' + @BlobUrl + '_Part3.bak?' + @SASToken + ''' ' -- Include SAS token
        + 'URL = ''' + @BlobUrl + '_Part4.bak?' + @SASToken + ''' ' -- Include SAS token
        + 'URL = ''' + @BlobUrl + '_Part5.bak?' + @SASToken + ''' ' -- Include SAS token
        + 'WITH
            INIT,
            COMPRESSION,
            STATS = 2, -- Show progress every 2%
            MAXTRANSFERSIZE = 4194304, -- 4MB chunks
            BLOCKSIZE = 65536, -- Adjust block size as needed
            CHECKSUM,
            FORMAT,
            MEDIANAME = ''AzureBlobBackup'',
            NAME = ''Full Backup of ' + @name + ''',
           SKIP,
            NOREWIND,
            NOUNLOAD,
            RETAINDAYS = ' + CAST(@retentionDays AS NVARCHAR);
    END
    
    EXEC sp_executesql @backupCommand;
    FETCH NEXT FROM db_cursor INTO @name;

END;

CLOSE db_cursor;
DEALLOCATE db_cursor;