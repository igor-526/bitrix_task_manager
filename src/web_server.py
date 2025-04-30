from flask import Flask, request
import logging

app = Flask("web_server")


@app.post("/install")
def hello_world():
    logging.log(logging.WARN, str(request.json))
    return ""
