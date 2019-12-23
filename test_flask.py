from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World1!"

if __name__ == "__main__":
    app.run(host='130.141.112.137')