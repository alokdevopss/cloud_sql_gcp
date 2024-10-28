
## google-api-python-client==2.97.0
## google-auth==2.22.0

import google.auth
from googleapiclient.discovery import build

def patch_sql_instance(request):
    project_id = 'your-project-id'  # Replace with your project ID
    instance_name = 'mydb'          # Replace with your Cloud SQL instance name
    ip_range = '30.40.89.0/24'      # Replace with the IP range you want to authorize

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
                        "value": ip_range
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
