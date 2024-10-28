## working
import requests
import google.auth
from googleapiclient.discovery import build
import mysql.connector
import json
from flask import jsonify

def get_egress_ip(request):
    # Use an API that returns the public IPv4 address
    response = requests.get('https://ipv4.icanhazip.com')
    ip = response.text.strip()  # Remove any extra whitespace or newlines
    return ip  # Return just the IP

def patch_sql_instance(ip):
    project_id = 'eco-emissary-415909'  # Replace with your project ID 
    instance_name = 'mydb'      # Replace with your Cloud SQL instance name

    # Get the credentials and project from the environment
    credentials, project = google.auth.default()

    # Build the SQL Admin service
    service = build('sqladmin', 'v1', credentials=credentials)

    # Define the body of the patch request
    body = {
        "settings": {
            "ipConfiguration": {
                "authorizedNetworks": [
                    {
                        "value": ip  # Use the IP here
                    }
                ]
            }
        }
    }

    # Call the patch method to update the authorized networks
    request = service.instances().patch(
        project=project_id,
        instance=instance_name,
        body=body
    )

    try:
        response = request.execute()
        return f"Patch successful: {response}"
    except Exception as e:
        return f"Error patching SQL instance: {str(e)}"

def connect_to_db():
    try:
        # MySQL connection configuration (direct values)
        connection = mysql.connector.connect(
            user='root',           # Replace with your MySQL username
            password='password',       # Replace with your MySQL password
            host='34.69.50.181',       # Replace with your Cloud SQL IP (public or private)
            database='mydb'   # Replace with your database name
        )
        # Check if the connection was successful
        if connection.is_connected():
            return {"status": "Connected"}, 200
        else:
            return {"status": "Not Connected"}, 500
    except mysql.connector.Error as err:
        # Return detailed error message
        return {"status": "Not Connected", "error": str(err)}, 500
    except Exception as e:
        # Catch any other exceptions and return the error message
        return {"status": "Internal Error", "error": str(e)}, 500
    finally:
        # Close the connection if it's open
        try:
            if connection.is_connected():
                connection.close()
        except NameError:
            # Connection was never initialized, nothing to close
            pass

def main(request):
    """Entry point for the Cloud Function."""
    # Step 1: Get the egress IP
    egress_ip = get_egress_ip(request)
    
    # Step 2: Patch the IP to Cloud SQL
    patch_result = patch_sql_instance(egress_ip)

    # Step 3: Attempt to connect to the Cloud SQL database
    db_connect_result, status_code = connect_to_db()
    
    # Return the results
    return jsonify({
        "egress_ip": egress_ip,
        "patch_result": patch_result,
        "db_connect_result": db_connect_result
    }), status_code

######################################################################################################################################################

# not working

import requests
import google.auth
from googleapiclient.discovery import build
import mysql.connector
import json
from flask import jsonify
import time  # For delay between patch and detach if necessary

def get_egress_ip():
    # Use an API that returns the public IPv4 address
    response = requests.get('https://ipv4.icanhazip.com')
    ip = response.text.strip()  # Remove any extra whitespace or newlines
    return ip  # Return just the IP

def patch_sql_instance(ip):
    project_id = 'eco-emissary-415909'  # Replace with your project ID 
    instance_name = 'mydb'  # Replace with your Cloud SQL instance name

    # Get the credentials and project from the environment
    credentials, project = google.auth.default()

    # Build the SQL Admin service
    service = build('sqladmin', 'v1', credentials=credentials)

    # Define the body of the patch request
    body = {
        "settings": {
            "ipConfiguration": {
                "authorizedNetworks": [
                    {
                        "value": ip  # Use the egress IP here
                    }
                ]
            }
        }
    }

    # Call the patch method to update the authorized networks
    patch_request = service.instances().patch(
        project=project_id,
        instance=instance_name,
        body=body
    )

    try:
        response = patch_request.execute()
        return f"Patch successful: {response}"
    except Exception as e:
        return f"Error patching SQL instance: {str(e)}"

def connect_to_db():
    try:
        # MySQL connection configuration (direct values)
        connection = mysql.connector.connect(
            user='root',           # Replace with your MySQL username
            password='password',   # Replace with your MySQL password
            host='34.69.50.181',   # Replace with your Cloud SQL IP (public or private)
            database='mydb'        # Replace with your database name
        )
        # Check if the connection was successful
        if connection.is_connected():
            return {"status": "Connected"}, 200
        else:
            return {"status": "Not Connected"}, 500
    except mysql.connector.Error as err:
        # Return detailed error message
        return {"status": "Not Connected", "error": str(err)}, 500
    except Exception as e:
        # Catch any other exceptions and return the error message
        return {"status": "Internal Error", "error": str(e)}, 500
    finally:
        # Close the connection if it's open
        try:
            if connection.is_connected():
                connection.close()
        except NameError:
            # Connection was never initialized, nothing to close
            pass

def detach_ip_from_sql_instance(ip):
    project_id = 'eco-emissary-415909'  # Replace with your project ID
    instance_name = 'mydb'              # Replace with your Cloud SQL instance name

    # Get the credentials and project from the environment
    credentials, project = google.auth.default()

    # Build the SQL Admin service
    service = build('sqladmin', 'v1', credentials=credentials)

    # First, fetch the current settings of the Cloud SQL instance
    try:
        instance = service.instances().get(
            project=project_id,
            instance=instance_name
        ).execute()

        # Extract the current authorized networks
        authorized_networks = instance['settings']['ipConfiguration'].get('authorizedNetworks', [])

        # Remove the specified IP from the authorized networks
        updated_networks = [network for network in authorized_networks if network['value'] != ip]

        # Define the body of the patch request with the updated networks
        body = {
            "settings": {
                "ipConfiguration": {
                    "authorizedNetworks": updated_networks
                }
            }
        }

        # Call the patch method to update the authorized networks
        detach_request = service.instances().patch(
            project=project_id,
            instance=instance_name,
            body=body
        )

        response = detach_request.execute()
        return f"IP {ip} detached successfully: {response}"
    except Exception as e:
        return f"Error detaching IP from SQL instance: {str(e)}"

def main(request):
    """Entry point for the Cloud Function."""
    # Step 1: Get the egress IP
    egress_ip = get_egress_ip()
    
    # Step 2: Patch the IP to Cloud SQL
    patch_result = patch_sql_instance(egress_ip)

    # Step 3: Attempt to connect to the Cloud SQL database
    db_connect_result, status_code = connect_to_db()

    # Optional: Wait for the patch to propagate (if needed, introduce a delay)
    # time.sleep(20)

    # Step 4: Detach the IP from Cloud SQL
    detach_result = detach_ip_from_sql_instance(egress_ip)
    
    # Return the results
    return jsonify({
        "egress_ip": egress_ip,
        "patch_result": patch_result,
        "db_connect_result": db_connect_result,
        "detach_result": detach_result
    }), status_code
