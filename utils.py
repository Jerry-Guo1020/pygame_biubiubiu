import os

def _score_path():
    return os.path.join(os.path.dirname(__file__), "max_score.txt")

def read_max_score():
    p = _score_path()
    try:
        with open(p, "r", encoding="utf-8") as f:
            v = int(f.read().strip() or "0")
            return max(0, v)
    except Exception:
        return 0

def save_max_score(score):
    try:
        cur = read_max_score()
        if score > cur:
            with open(_score_path(), "w", encoding="utf-8") as f:
                f.write(str(int(score)))
    except Exception:
        pass

def cut_number(num):
    try:
        n = int(num)
    except Exception:
        n = 0
    if n < 0: n = 0
    if n > 999: n = 999
    h = (n // 100) % 10
    t = (n // 10) % 10
    s = n % 10
    return h, t, s
