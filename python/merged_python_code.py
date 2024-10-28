import google.auth
from googleapiclient.discovery import build
import mysql.connector
import json

# google-auth==2.20.0
# google-api-python-client==2.64.0
# mysql-connector-python==8.0.33


# Replace these variables with your actual values
PROJECT_ID = 'project_ID'
INSTANCE_NAME = 'mydb'
IP_RANGE = ''
DB_USER = 'root'
DB_PASSWORD = 'password'
DB_HOST = ''
DB_NAME = 'mydb'
IP_TO_DETACH = ''

def patch_sql_instance():
    """Patches the Cloud SQL instance to add an authorized IP range."""
    credentials, project = google.auth.default()
    service = build('sqladmin', 'v1', credentials=credentials)
    body = {
        "settings": {
            "ipConfiguration": {
                "authorizedNetworks": [
                    {
                        "value": IP_RANGE
                    }
                ]
            }
        }
    }
    request = service.instances().patch(
        project=PROJECT_ID,
        instance=INSTANCE_NAME,
        body=body
    )
    try:
        response = request.execute()
        return f"Patch successful: {response}"
    except Exception as e:
        return f"Error patching SQL instance: {str(e)}"

def connect_to_db():
    """Tries to connect to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME
        )
        if connection.is_connected():
            return "Connected to DB"
        else:
            return "Failed to connect to DB"
    except mysql.connector.Error as err:
        return f"MySQL connection error: {str(err)}"
    except Exception as e:
        return f"General error: {str(e)}"
    finally:
        try:
            if connection.is_connected():
                connection.close()
        except NameError:
            pass

def detach_ip_from_sql_instance():
    """Detaches the authorized IP range from Cloud SQL instance."""
    credentials, project = google.auth.default()
    service = build('sqladmin', 'v1', credentials=credentials)
    try:
        instance = service.instances().get(
            project=PROJECT_ID,
            instance=INSTANCE_NAME
        ).execute()

        authorized_networks = instance['settings']['ipConfiguration'].get('authorizedNetworks', [])
        updated_networks = [network for network in authorized_networks if network['value'] != IP_TO_DETACH]

        body = {
            "settings": {
                "ipConfiguration": {
                    "authorizedNetworks": updated_networks
                }
            }
        }

        request = service.instances().patch(
            project=PROJECT_ID,
            instance=INSTANCE_NAME,
            body=body
        )

        response = request.execute()
        return f"IP {IP_TO_DETACH} detached successfully: {response}"
    except Exception as e:
        return f"Error detaching IP from SQL instance: {str(e)}"

def main(request):
    """Entry point for the Cloud Function."""
    # Step 1: Patch the IP to Cloud SQL
    patch_result = patch_sql_instance()
    
    # Step 2: Attempt to connect to the Cloud SQL database
    connect_result = connect_to_db()
    
    # Step 3: Detach the IP from Cloud SQL
    detach_result = detach_ip_from_sql_instance()
    
    # Return the results of all three steps
    return json.dumps({
        "patch_result": patch_result,
        "connect_result": connect_result,
        "detach_result": detach_result
    })
