
# APIKEY
url = "https://example.com/api/resource"
headers = {
    "Authorization": f"api-key {api_key}"
}
response = requests.get(url, headers=headers)

# TOKEN
url = "https://example.com"
headers = {
    "Authorization": f"Bearer {access_token}"
}
response = requests.get(url, headers=headers)

# BEARER

# BASIC
# Use the following format for the username and password: "username:password"
# Basic authentication is the simplest form of authentication, and involves
# sending a username and password with each request.
# This is generally done using the HTTP authorization header,
# and the credentials are encoded using Base64.
url = "https://example.com"
credentials = "user:pass"
headers = {
    "Authorization": f"Basic {credentials}"
}
response = requests.get(url, headers=headers)
