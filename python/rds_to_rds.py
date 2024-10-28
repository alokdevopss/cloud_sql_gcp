import pymysql
import os

# Source RDS
src_host = os.environ['SRC_HOST']
src_user = os.environ['SRC_USER']
src_password = os.environ['SRC_PASSWORD']
src_db = os.environ['SRC_DB']

# Target RDS
tgt_host = os.environ['TGT_HOST']
tgt_user = os.environ['TGT_USER']
tgt_password = os.environ['TGT_PASSWORD']
tgt_db = os.environ['TGT_DB']

def lambda_handler(event, context):
    # Connect to source database
    src_conn = pymysql.connect(host=src_host, user=src_user, password=src_password, db=src_db)
    src_cursor = src_conn.cursor()
    src_cursor.execute("SELECT * FROM your_table")

    # Fetch all rows
    rows = src_cursor.fetchall()

    # Connect to target database
    tgt_conn = pymysql.connect(host=tgt_host, user=tgt_user, password=tgt_password, db=tgt_db)
    tgt_cursor = tgt_conn.cursor()

    # Insert data into target database
    for row in rows:
        tgt_cursor.execute("INSERT INTO your_table VALUES (%s, %s, %s)", row)

    # Commit and close connections
    tgt_conn.commit()
    src_conn.close()
    tgt_conn.close()
