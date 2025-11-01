import math

def recognize_pattern(points, pattern="square"):

    prediction = False

    if pattern == "square":
        prediction = recognize_square(points)
    elif pattern == "triangle":
        prediction = recognize_triangle(points)
    elif pattern == "circle":
        prediction = recognize_circle(points)
    elif pattern == "z":
        prediction = recognize_z(points)

    return prediction


def identify_pattern(points):
    """Try to identify which known pattern (if any) the stroke matches.

    Returns a tuple (matched: bool, pattern: str|None).
    """
    # check each known pattern in a reasonable order
    for p in ("square", "triangle", "circle", "z"):
        try:
            if recognize_pattern(points, pattern=p):
                return True, p
        except Exception:
            # if a specific recognizer errors, skip it
            continue
    return False, None

def recognize_square(points):
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


def recognize_triangle(points):
    """Detect a roughly triangular stroke using corner counting and bounding box checks."""
    if not points or len(points) < 6:
        return False

    pts = [(float(x), float(y)) for x, y in points]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = maxx - minx
    h = maxy - miny
    diag = math.hypot(w, h)
    if diag == 0:
        return False

    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    if end_dist > diag * 0.35:
        return False

    # sample
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]

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

    corners = 0
    for i in range(1, len(sampled) - 1):
        a = sampled[i - 1]
        b = sampled[i]
        c = sampled[i + 1]
        ang = angle(a, b, c)
        if ang > 30 and ang < 150:
            corners += 1

    # expect around 3 corners
    if not (2 <= corners <= 4):
        return False

    # aspect ratio tolerant
    if w == 0 or h == 0:
        return False
    ar = max(w, h) / min(w, h)
    if ar > 2.5:  # triangles can be tall or wide, allow more deviation
        return False

    return True


def recognize_circle(points):
    """Detect a roughly circular stroke by checking closure and radial variance around centroid."""
    if not points or len(points) < 12:
        return False

    pts = [(float(x), float(y)) for x, y in points]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = maxx - minx
    h = maxy - miny
    diag = math.hypot(w, h)
    if diag == 0:
        return False

    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    if end_dist > diag * 0.45:
        return False

    # centroid
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    dists = [math.hypot(p[0] - cx, p[1] - cy) for p in pts]
    mean_r = sum(dists) / len(dists)
    if mean_r == 0:
        return False
    # radial variance (normalized)
    var = sum((d - mean_r) ** 2 for d in dists) / len(dists)
    std = math.sqrt(var)
    if std / mean_r > 0.35:
        return False

    # bounding box should be reasonably square for circle
    ar = max(w, h) / min(w, h) if (w and h) else float('inf')
    if ar > 1.6:
        return False

    return True


def recognize_z(points):
    """Detecta um traço similar a um 'Z' usando contagem de cantos e verificação de bounding box."""
    
    # 1. Pré-processamento
    if not points or len(points) < 6:
        return False

    pts = [(float(x), float(y)) for x, y in points]

    # 2. Bounding Box & Diagonal
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = maxx - minx
    h = maxy - miny
    diag = math.hypot(w, h)
    if diag == 0:
        return False

    # 3. Verificação de Ponto Inicial/Final (ADAPTADO para 'Z')
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    if end_dist < diag * 0.5:  # O traço deve ser aberto (distância > 50% da diagonal)
        return False

    # 4. Reamostragem
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]

    # 5. Detecção de Cantos
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

    corners = 0
    for i in range(1, len(sampled) - 1):
        a = sampled[i - 1]
        b = sampled[i]
        c = sampled[i + 1]
        ang = angle(a, b, c)
        if 30 < ang < 150:
            corners += 1

    # 6. Verificações Geométricas (Contagem de Cantos)
    if not (2 <= corners <= 3):
        return False

    # 7. Verificações Geométricas (Proporção)
    if w == 0 or h == 0:
        return False
    ar = max(w, h) / min(w, h)
    if ar > 2.5:
        return False

    # Se passou em todas as verificações, é provável que seja um 'Z'
    return True

