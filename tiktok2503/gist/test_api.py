import requests

def get_access_token(client_key, client_secret):
    # Endpoint URL
    endpoint_url = "https://open.tiktokapis.com/v2/oauth/token/"

    # Request headers
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # Request body parameters
    data = {
        'client_key': client_key,
        'client_secret': client_secret,
        'grant_type': 'client_credentials',
    }

    # Make the POST request
    response = requests.post(endpoint_url, headers=headers, data=data)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse and print the response JSON
        response_json = response.json()
        print("Access Token:", response_json['access_token'])
        print("Expires In:", response_json['expires_in'])
        print("Token Type:", response_json['token_type'])
    else:
        # If the request was not successful, print the error response JSON
        print("Error:", response.json())

# Replace with your actual client key and client secret
client_key = "yours"
client_secret = "yours"

# Call the function with your credentials
get_access_token(client_key, client_secret)