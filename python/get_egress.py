import requests

def get_egress_ip(request):
    # Use an API that returns the public IPv4 address
    response = requests.get('https://ipv4.icanhazip.com')
    ip = response.text.strip()  # Remove any extra whitespace or newlines
    return f"Egress IP (IPv4): {ip}"



