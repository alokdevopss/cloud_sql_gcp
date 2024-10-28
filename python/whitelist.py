import requests
import googleapiclient.discovery
import mysql.connector
from flask import jsonify, Request

def get_egress_ip() -> str:
    """Fetch the public IPv4 address of the Cloud Function."""
    response = requests.get('https://ipv4.icanhazip.com')
    ip = response.text.strip()  # Remove any extra whitespace or newlines
    return ip

def whitelist_ip(ip: str) -> None:
    """Whitelist the egress IP in the Cloud SQL instance."""
    service = googleapiclient.discovery.build('sqladmin', 'v1beta4')
    project_id = 'eco-emissary-415909'
    instance_id = 'mydb'
    
    # Fetch current authorized networks
    instance = service.instances().get(project=project_id, instance=instance_id).execute()
    authorized_networks = instance.get('settings', {}).get('authorizedNetworks', [])

    # Check if the IP is already whitelisted
    if any(network['value'] == ip for network in authorized_networks):
        return

    # Add the new IP to the authorized networks
    authorized_networks.append({
        'name': 'dynamic-whitelist',
        'value': ip
    })

    service.instances().patch(
        project=project_id,
        instance=instance_id,
        body={
            'settings': {
                'authorizedNetworks': authorized_networks
            }
        }
    ).execute()

# def connect_to_db() -> jsonify:
#     """Connect to the MySQL database and return connection status."""
#     try:
#         connection = mysql.connector.connect(
#             user='root',           # Replace with your MySQL username
#             password='password',       # Replace with your MySQL password
#             host='35.200.215.31',       # Replace with your Cloud SQL IP (public or private)
#             database='mydb'   # Replace with your database name
#         )
#         # Check if the connection was successful
#         if connection.is_connected():
#             return jsonify(status="Connected"), 200
#         else:
#             return jsonify(status="Not Connected"), 500
#     except mysql.connector.Error as err:
#         # Return detailed error message
#         return jsonify(status="Not Connected", error=str(err)), 500
#     except Exception as e:
#         # Catch any other exceptions and return the error message
#         return jsonify(status="Internal Error", error=str(e)), 500
#     finally:
#         # Close the connection if it's open
#         try:
#             if connection.is_connected():
#                 connection.close()
#         except NameError:
#             # Connection was never initialized, nothing to close
#             pass

def cloud_function_entry(request: Request) -> jsonify:
    """Main entry point for the Cloud Function."""
    ip = get_egress_ip()
    whitelist_ip(ip)
    
    # Allow some time for the IP whitelisting to propagate
    # This is a simple sleep; consider implementing a retry mechanism in production
    import time
    time.sleep(10)  # Sleep for 10 seconds to ensure IP whitelisting is effective
    
    # Then, connect to the database
    # db_result = connect_to_db()
    # return jsonify(result="Egress IP whitelisted and ready to use.", db_status=db_result.get_json())
