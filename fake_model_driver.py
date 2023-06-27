import requests, random, signal, time
from requests.auth import HTTPDigestAuth
from threading import Timer
from model import diff

random.seed()

auth = HTTPDigestAuth("jonty", "foo")


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Odds:
    def __init__(self, num, denom):
        self.numerator = num  # top
        self.denominator = denom  # bottom

    def random_move(self):
        num_mode = -1 if self.numerator > 4 else 0
        denom_mode = -2 if self.denominator > 10 else 0
        num_move = int(round(random.triangular(-2, 2, num_mode), 0))
        denom_move = int(round(random.triangular(-2, 2, denom_mode), 0))

        if num_move < 0:
            num_move = 0

        if num_move == 0 and denom_move == 0:
            # eh, just fudge it so something changes
            denom_move = 1

        return Odds(self.numerator + num_move, self.denominator + denom_move)

    def check(self):
        return self.numerator >= 0 and self.denominator >= 0

    def __str__(self):
        return "{}/{}".format(self.numerator, self.denominator)


def gen_odds():
    num = int(round(random.triangular(1, 6, 1), 0))
    denom = random.randint(1, 20)
    return Odds(num, denom)


class Model:
    def __init__(self, names):
        self.model = {name: gen_odds() for name in names}

    def modify_random(self):
        name = random.choice(list(self.model.keys()))
        tries = 0
        max_tries = 5
        while tries < max_tries:
            new_odds = self.model[name].random_move()
            if new_odds.check():
                break
            else:
                new_odds = None
                tries += 1

        if new_odds is not None:
            self.model[name] = new_odds
            diff = {"lost": [], "new": {}, "changed": {name: str(new_odds)}}
            return diff
        else:
            print(
                "Failed to get a valid new random odds after {} tries".format(max_tries)
            )
            return None

    def snapshot(self):
        return {k: str(v) for k, v in self.model.items()}


def send_diff(diff):
    payload = {"diff": diff}
    r = requests.post(
        "http://127.0.0.1:5000/model/api/v1.0/diff", json=payload, auth=auth
    )
    print("Sent Diff:\n>>{}\n>>{}\n>>{}".format(payload, r, r.text))


def send_snapshot(snap):
    payload = {"snapshot": snap}
    r = requests.post(
        "http://127.0.0.1:5000/model/api/v1.0/snapshot", json=payload, auth=auth
    )
    print("Sent Snapshot:\n>>{}\n>>{}\n>>{}".format(payload, r, r.text))


def modify_and_send(model):
    diff = model.modify_random()
    print(diff)
    if diff is not None:
        send_diff(diff)


def main():
    model = Model(["Tim", "Sam", "Jenny", "Krang destroyer of all"])
    send_snapshot(model.snapshot())
    timer = RepeatTimer(2, modify_and_send, args=[model])
    timer.start()
    try:
        while True:
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("Interrupted")
    timer.cancel()


if __name__ == "__main__":
    main()

