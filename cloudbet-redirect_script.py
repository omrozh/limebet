import flask
import requests
import json

from urllib.parse import unquote

api_key = "eyJhbGciOiJSUzI1NiIsImtpZCI6IkhKcDkyNnF3ZXBjNnF3LU9rMk4zV05pXzBrRFd6cEdwTzAxNlRJUjdRWDAiLCJ0eXAiOiJKV1QifQ.eyJhY2Nlc3NfdGllciI6InRyYWRpbmciLCJleHAiOjIwMzAyMTQ0NDksImlhdCI6MTcxNDg1NDQ0OSwianRpIjoiMmJkMzZmN2MtYzJmZS00ZDYyLTljMmYtNzhlZjUyNTZiODQ0Iiwic3ViIjoiZGMxZmU0MzEtZTU5Ny00YjhiLWE5M2UtZTNmODk1OTI5MDhkIiwidGVuYW50IjoiY2xvdWRiZXQiLCJ1dWlkIjoiZGMxZmU0MzEtZTU5Ny00YjhiLWE5M2UtZTNmODk1OTI5MDhkIn0.PjaTkALsZoozFO7P3nUsmL1JFz02t5qpmafrMFqror1xKYYVRHsddZxcs73sOtIO_P-cFlmaHxVXvPUw9CaeOqUQmF6_IeCJBycjNhviTFVMcXdq7dF2Z-Elsa5dKlPdQooRFv_8wUJ5dxY8bkIgXfKRoizU_1lOeEJ2HaLp3UmRhqBcX_aietQ4dYu4DapIuOkm93nDnGoCArLtnqBCfiaWTMIBwdOtWVrgV90M256iSTgpAsI0xkVmqrLZJqfnKOVvZ1DnwcmPYPgC4i6nsG-1C24s3Mse0Dw_hFE7svR_S5QhK-hLONbOUKrKF_WLntrRXrIbwYGfX8IMWYOCFg"

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
        dictionary_out[i.split("=")[0]] = unquote(i.split("=")[1])

    dictionary_out = json.dumps(dictionary_out)

    response = requests.post(trading_url, headers=headers, data=dictionary_out)
    return flask.jsonify(response.json())


@app.route("/check/bet/<bet_reference_id>")
def check_bet(bet_reference_id):
    odd_url = f"https://sports-api.cloudbet.com/pub/v3/bets/{bet_reference_id}/status"
    headers = {
        "accept": "application/json",
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    response = requests.get(odd_url, headers=headers)
    return flask.jsonify(response.json())
