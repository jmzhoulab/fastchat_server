from flask import Flask
from controller.controller import fastChatModule

app = Flask(__name__)
app.register_blueprint(fastChatModule, url_prefix='/fastchat')


@app.route('/')
def hello_world():
    return 'flask_test is running!!!'


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7801)

