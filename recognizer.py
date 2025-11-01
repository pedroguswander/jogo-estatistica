import math


def recognize_pattern(points):
    """Very small recognizer that tries to detect a roughly-square stroke.

    Heuristics used:
    - require enough points
    - start and end must be near (closed stroke)
    - count of sharp turns (corners) should be ~4
    - bounding-box aspect ratio should be near 1 (square-like)

    Returns True if a square-like shape is detected.
    """
    if not points or len(points) < 8:
        return False

    # convert points to floats
    pts = [(float(x), float(y)) for x, y in points]

    # bounding box
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = maxx - minx
    h = maxy - miny
    diag = math.hypot(w, h)
    if diag == 0:
        return False

    # start-end closure: distance should be small relative to diag
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    if end_dist > diag * 0.35:
        return False

    # sample to reduce noise
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]

    # helper: angle at b between a-b-c
    def angle(a, b, c):
        bax = a[0] - b[0]
        bay = a[1] - b[1]
        bcx = c[0] - b[0]
        bcy = c[1] - b[1]
        da = math.hypot(bax, bay)
        db = math.hypot(bcx, bcy)
        if da == 0 or db == 0:
            return 0.0
        dot = (bax * bcx + bay * bcy) / (da * db)
        dot = max(-1.0, min(1.0, dot))
        return math.degrees(math.acos(dot))

    # count sharp turns
    corners = 0
    for i in range(1, len(sampled) - 1):
        a = sampled[i - 1]
        b = sampled[i]
        c = sampled[i + 1]
        ang = angle(a, b, c)
        # for a corner in a square the interior angle is ~90, external turn ~90 as well
        if ang > 45 and ang < 135:
            corners += 1

    # we expect roughly 4 corners (allow some tolerance)
    if not (3 <= corners <= 6):
        return False

    # aspect ratio check: square should have ar not too far from 1
    if w == 0 or h == 0:
        return False
    ar = max(w, h) / min(w, h)
    if ar > 1.6:  # allow 60% deviation
        return False

    return True
