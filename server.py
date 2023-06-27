import flask
from flask_socketio import SocketIO, send, emit
from flask_httpauth import HTTPDigestAuth
from model import Model

app = flask.Flask(__name__, static_url_path="")
app.config["SECRET_KEY"] = "qwdinqwodqkim"
socketio = SocketIO(app)
auth = HTTPDigestAuth()

model = Model(socketio)
users = {"jonty": "foo", "david": "bar"}


@auth.get_password
def get_pw(user):
    if user in users:
        return users[user]


@app.route("/")
def index():
    print("Index?")
    return app.send_static_file("frontend.html")


@app.route("/foo")
@auth.login_required
def incr_foo():
    print("Incrementing Foo")
    f = model.odds_clone()
    f["foo"] = f["foo"] + 1
    print("New model: {}".format(f))
    model.smash_and_broadcast(f)
    print("Update done")
    return "Done that for u"


@auth.login_required
@app.route("/model/api/v1.0/diff", methods=["POST"])
def diff():
    if not flask.request.json or "diff" not in flask.request.json:
        flask.abort(400)
    model.apply_diff_and_broadcast(flask.request.json["diff"])
    return flask.jsonify({"success": True}), 201


@auth.login_required
@app.route("/model/api/v1.0/snapshot", methods=["POST"])
def snapshot():
    print(flask.request)
    if not flask.request.json or "snapshot" not in flask.request.json:
        flask.abort(400)
    model.smash_and_broadcast(flask.request.json["snapshot"])
    return flask.jsonify({"success": True}), 201


@socketio.on("connect")
def handle_connect():
    print("Connection established")


@socketio.on("message")
def handle_message(message):
    print("received message: " + message)


@socketio.on("json")
def handle_json(json):
    print("received json: " + str(json))


@socketio.on("snapshot_request")
def handle_my_snapshot_request():
    print("received snapshot request")
    emit("model_snapshot", model.snapshot())


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0")
