_score = 0

def increment_score(points):
    global _score
    _score += points

def init_score(points):
    global _score
    _score = points

def get_score():
    return _score

def reset_score():
    global _score
    _score = 0