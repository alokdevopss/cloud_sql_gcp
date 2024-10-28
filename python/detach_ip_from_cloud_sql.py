import google.auth
from googleapiclient.discovery import build

def detach_ip_from_sql_instance(request):
    project_id = 'project_id'  # Replace with your project ID
    instance_name = 'mydb'          # Replace with your Cloud SQL instance name
    ip_to_detach = '30.40.89.0/24'  # Replace with the IP range you want to remove

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
        updated_networks = [network for network in authorized_networks if network['value'] != ip_to_detach]

        # Define the body of the patch request with the updated networks
        body = {
            "settings": {
                "ipConfiguration": {
                    "authorizedNetworks": updated_networks
                }
            }
        }

        # Call the patch method to update the authorized networks
        request = service.instances().patch(
            project=project_id,
            instance=instance_name,
            body=body
        )

        response = request.execute()
        return f"IP {ip_to_detach} detached successfully: {response}"
    except Exception as e:
        return f"Error detaching IP from SQL instance: {str(e)}"
