import flask
import requests
import json

api_key = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkhKcDkyNnF3ZXBjNnF3LU9rMk4zV05pXzBrRFd6cEdwTzAxNlRJUjdRWDAiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6InRyYWRpbmciLCJleHAiOjIwMjgwNDU1ODksImlhdCI6MTcxMjY4NTU4OSwianRpIjoiYjIxZGRjZGYtZjZmNy00NTg1LWFlZDItOTVhNTkwMmU2YmUxIiwic3ViIjoiMzEyMTg1NDgtY2U3MS00NWJiLTlmNTctNmE4YmI3NTI5NjY2IiwidGVuYW50IjoiY2xvdWRiZXQiLCJ1dWlkIjoiMzEyMTg1NDgtY2U3MS00NWJiLTlmNTctNmE4YmI3NTI5NjY2In0.1e8o2kkX_UEccVndkKZDUS0IER6pFJPaSpIR3dzb486PyfpbFq82UggU6goIj9g7hns8sB1HNV__9U6XXLStE_x2qWDd2ZoFwMTeZeuGyMBFqdUK3Z-GGAg-_uYr3wqRB9QbhHHrS_BXEyTpRoxuGLncY8Yq87XuyfH0KbTAjexJOqd6RoseKGLnkex2mAaCc53CrLJh2ysq8wvLtRAYDxCQQN7eCbhRm58TDjTFZKU49u3kokNy4JuwLgjubcqC7F1ibYXwLMGPYH6kSN2zkApje_kmw3SSpJ3HqXptfdy1bIsV-GvlSXStpFnz7btp2Jj2Dhv4E4Hqclt8bRQRng"

app = flask.Flask(__name__)


@app.route("/place/bet", methods=["POST"])
def place_bet():
    trading_url = "https://sports-api.cloudbet.com/pub/v3/bets/place"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    data = flask.request.data.decode("utf-8")
    dictionary_out = {}
    for i in data.split("&"):
        dictionary_out[i.split("=")[0]] = i.split("=")[1].replace("%2F", "/").replace("%3F", "?").replace("%3D", "=")

    dictionary_out = json.dumps(dictionary_out)

    response = requests.post(trading_url, headers=headers, data=dictionary_out)
    return flask.jsonify(response.json())
