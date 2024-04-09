import requests
import json

event_url = "https://sports-api.cloudbet.com/pub/v2/odds/events?sport=soccer&live=false&limit=100&from=1712653333&to=1712685805"
api_key = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkhKcDkyNnF3ZXBjNnF3LU9rMk4zV05pXzBrRFd6cEdwTzAxNlRJUjdRWDAiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6InRyYWRpbmciLCJleHAiOjIwMjgwNDU1ODksImlhdCI6MTcxMjY4NTU4OSwianRpIjoiYjIxZGRjZGYtZjZmNy00NTg1LWFlZDItOTVhNTkwMmU2YmUxIiwic3ViIjoiMzEyMTg1NDgtY2U3MS00NWJiLTlmNTctNmE4YmI3NTI5NjY2IiwidGVuYW50IjoiY2xvdWRiZXQiLCJ1dWlkIjoiMzEyMTg1NDgtY2U3MS00NWJiLTlmNTctNmE4YmI3NTI5NjY2In0.1e8o2kkX_UEccVndkKZDUS0IER6pFJPaSpIR3dzb486PyfpbFq82UggU6goIj9g7hns8sB1HNV__9U6XXLStE_x2qWDd2ZoFwMTeZeuGyMBFqdUK3Z-GGAg-_uYr3wqRB9QbhHHrS_BXEyTpRoxuGLncY8Yq87XuyfH0KbTAjexJOqd6RoseKGLnkex2mAaCc53CrLJh2ysq8wvLtRAYDxCQQN7eCbhRm58TDjTFZKU49u3kokNy4JuwLgjubcqC7F1ibYXwLMGPYH6kSN2zkApje_kmw3SSpJ3HqXptfdy1bIsV-GvlSXStpFnz7btp2Jj2Dhv4E4Hqclt8bRQRng"

event_id = 123456
headers = {
    "accept": "application/json",
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

try:
    response = requests.get(event_url.format(event_id), headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    event_data = response.json()
    print(json.dumps(event_data, indent=4))
except requests.exceptions.RequestException as e:
    print("Error:", e)
