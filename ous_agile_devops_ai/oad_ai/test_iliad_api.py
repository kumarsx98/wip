import requests

def test_iliad_api():
    api_url = "http://iliadtools.raiders-dev.awscloud.abbvienet.com:8234"
    api_key = "B1xJInq9KnjrEurPCS3N1K9I1KNyyvIh"  # Replace with your actual API key
    headers = {
        'Authorization': f'Bearer {api_key}'  # Adjust this according to the API's requirements
    }
    try:
        response = requests.get(api_url, headers=headers, allow_redirects=True)
        if response.status_code == 200:
            print("Successfully connected to the API.")
            print("Response:", response.text)
        else:
            print(f"Failed to connect to the API. Status code: {response.status_code}")
            print("Response:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_iliad_api()
