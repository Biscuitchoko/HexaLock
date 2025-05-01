import os
from flask import Flask # type: ignore

app = Flask(__name__)

@app.route('/')
def home():
    return "HexaLock bot is running!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
