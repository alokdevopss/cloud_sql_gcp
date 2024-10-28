import subprocess

def curl_vm():
    # Replace with your VM's IP or URL
    url = "http://34.67.210.188"

    # Curl command to fetch data from the VM
    cmd = f"curl {url}"

    try:
        # Execute the curl command and get the output
        output = subprocess.check_output(cmd, shell=True)
        # Print the output
        print(output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.output.decode('utf-8')}")

curl_vm()

import subprocess

def curl_vm():
    # Replace with your VM's IP or URL
    url = "http://34.87.210.34"

    # Curl command to fetch data from the VM
    cmd = ["curl", url]

    try:
        # Execute the curl command and get the output
        output = subprocess.check_output(cmd)
        # Print the output
        print(output.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.output.decode('utf-8')}")

curl_vm()
