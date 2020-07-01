from flask import Flask
from flask_sslify import SSLify


app = Flask(__name__)
sslify = SSLify(app)

@app.route('/')
def index():
    return '<h1> My app </h1>'


if __name__ == '__main__':
    app.run()