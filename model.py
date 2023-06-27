def diff(from_, to_):
    print("Diffing {}, {}".format(from_, to_))
    from_keys = set(from_.keys())
    to_keys = set(to_.keys())

    kept_keys = from_keys.intersection(to_keys)
    lost_keys = from_keys - to_keys
    added_keys = to_keys - from_keys

    lost = list(lost_keys)
    new = {key: to_[key] for key in added_keys}
    changed = {key: to_[key] for key in kept_keys if from_[key] != to_[key]}

    if len(lost) + len(new) + len(changed) == 0:
        return None
    else:
        return {"lost": lost, "new": new, "changed": changed}


class Model:
    def __init__(self, socketio_app):
        self.odds = {}
        self.socketio_app = socketio_app

    def apply_diff_and_broadcast(self, diff):
        for k, v in diff["new"].items():
            self.odds[k] = v
        for k, v in diff["changed"].items():
            self.odds[k] = v
        for k in diff["lost"]:
            del self.odds[k]

        print("Broadcasting model diff: {}".format(diff))
        self.socketio_app.emit("model_diff", diff)

    def smash_and_broadcast(self, new_model):
        diff_ = diff(self.odds, new_model)
        print("Update. Diff: {}".format(diff_))
        if diff_ is not None:
            self.odds = new_model
            print("Broadcasting model diff: {}".format(diff_))
            self.socketio_app.emit("model_diff", diff_)

    def snapshot(self):
        return self.odds

    def odds_clone(self):
        return {k: v for k, v in self.odds.items()}


if __name__ == "__main__":
    from_ = {"a": 1, "b": 2, "c": 3}
    to_ = {"b": 2, "c": 200, "d": 10}
    print(diff(from_, to_))
