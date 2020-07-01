import flask

server = flask.Flask(__name__)

@server.route('/')
def index():
    return '<h1> My app </h1>'


if __name__ == '__main__':
    server.run()
