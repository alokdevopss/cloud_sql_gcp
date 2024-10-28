import mysql.connector
from flask import jsonify

def connect_to_db(request):
    try:
        # MySQL connection configuration using Cloud SQL Auth Proxy
        connection = mysql.connector.connect(
            user='root',           # Replace with your MySQL username
            password='password',   # Replace with your MySQL password
            database='mydb',       # Replace with your database name
            unix_socket='/cloudsql/project_id:region:db_name'  # Replace with your Cloud SQL instance connection name
        )
        
        # Check if the connection was successful
        if connection.is_connected():
            return jsonify(status="Connected"), 200
        else:
            return jsonify(status="Not Connected"), 500
    except mysql.connector.Error as err:
        # Return detailed error message
        return jsonify(status="Not Connected", error=str(err)), 500
    except Exception as e:
        # Catch any other exceptions and return the error message
        return jsonify(status="Internal Error", error=str(e)), 500
    finally:
        # Close the connection if it's open
        try:
            if connection.is_connected():
                connection.close()
        except NameError:
            # Connection was never initialized, nothing to close
            pass
