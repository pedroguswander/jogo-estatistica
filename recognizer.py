import math

def recognize_pattern(points, pattern="square"):

    prediction = False

    if pattern == "square":
        prediction = recognize_square(points)
    elif pattern == "circle":
        prediction = recognize_circle(points)
    #elif pattern == "v":
     #   prediction = recognize_v(points)
    elif pattern == "horizontal_line":
        prediction = recognize_horizontal_line(points)
    elif pattern == "vertical_line":
        prediction = recognize_vertical_line(points)
    elif pattern == "caret":
        prediction = recognize_caret(points)
    elif pattern == "l":
        prediction = recognize_caret(points)

    return prediction


def identify_pattern(points):
    """Try to identify which known pattern (if any) the stroke matches.

    Returns a tuple (matched: bool, pattern: str|None).
    """
    # check each known pattern in a reasonable order
    for p in ("square", "circle", "v", "l", "caret", "horizontal_line", "vertical_line"):
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

def recognize_circle(points):
    """
    Detecta um traço circular que está "muito perto de fechar",
    verificando fechamento, variância radial e proporção.
    """
    
    # 1. Pré-processamento e Bounding Box
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
    
    # 2. Verificação de Fechamento (AJUSTADA)
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    
    # Para ser "muito perto de fechar", a distância entre o início
    # e o fim deve ser pequena.
    # Se a distância for maior que 25% da diagonal, consideramos
    # que está muito aberto e rejeitamos.
    if end_dist > diag * 0.25:
        return False

    # 3. Verificação de "Circularidade" (Variância Radial)
    # Centróide
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    dists = [math.hypot(p[0] - cx, p[1] - cy) for p in pts]
    mean_r = sum(dists) / len(dists)
    
    if mean_r == 0:
        return False
        
    # Variância radial (normalizada)
    var = sum((d - mean_r) ** 2 for d in dists) / len(dists)
    std = math.sqrt(var)
    
    # Se o desvio padrão for > 35% do raio médio, não é redondo.
    if std / mean_r > 0.35:
        return False

    # 4. Verificação de Proporção (Aspect Ratio)
    # A "caixa" ainda deve ser razoavelmente quadrada.
    ar = max(w, h) / min(w, h) if (w and h) else float('inf')
    if ar > 1.6:
        return False

    return True

def recognize_v(points):
    """Detecta um traço similar a um 'V' (ou '^') usando contagem de cantos."""
    
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

    # 3. Verificação de Ponto Inicial/Final (ADAPTADO para 'V')
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    # Um 'V' é uma forma aberta, então os pontos inicial e final devem ser distantes
    if end_dist < diag * 0.4: 
        return False

    # 4. Reamostragem
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]

    # 5. Detecção de Cantos (Helper)
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

    # 6. Contagem de Cantos
    corners = 0
    # Precisa de pelo menos 3 pontos na amostra para calcular um ângulo
    if len(sampled) < 3:
         return False
         
    for i in range(1, len(sampled) - 1):
        a = sampled[i - 1]
        b = sampled[i]
        c = sampled[i + 1]
        ang = angle(a, b, c)
        # Procurando por uma curva acentuada
        if 30 < ang < 140:
            corners += 1

    # 7. Verificações Geométricas (Contagem de Cantos)
    # A principal característica de um 'V' é ter *um* canto principal.
    # Permitimos 2 para lidar com algum ruído no traço.
    if not (1 <= corners <= 2):
        return False

    # 8. Verificações Geométricas (Proporção)
    if w == 0 or h == 0:
        return False
    ar = max(w, h) / min(w, h)
    # Um 'V' pode ser largo ou estreito, então somos tolerantes
    if ar > 3.0: 
        return False

    # Se passou em todas as verificações, é provável que seja um 'V'
    return True

def recognize_caret(points):
    """Detecta um traço '^' (V invertido) verificando 1 canto principal no TOPO."""
    
    # 1. Pré-processamento e Bounding Box
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
    
    # Se não houver diagonal, ou não houver altura, não pode ser um caret
    if diag == 0 or h == 0:
        return False

    # 2. Verificação de Forma Aberta
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    if end_dist < diag * 0.4: 
        return False

    # 3. Reamostragem
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]
    if len(sampled) < 3:
         return False

    # 4. Helper de Ângulo
    def angle(a, b, c):
        bax = a[0] - b[0]
        bay = a[1] - b[1]
        bcx = c[0] - b[0]
        bcy = c[1] - b[1]
        da = math.hypot(bax, bay)
        db = math.hypot(bcx, bcy)
        if da == 0 or db == 0: return 0.0
        dot = max(-1.0, min(1.0, (bax * bcx + bay * bcy) / (da * db)))
        return math.degrees(math.acos(dot))

    # 5. Contagem de Cantos
    sharp_corners = []
    for i in range(1, len(sampled) - 1):
        a = sampled[i - 1]
        b = sampled[i]
        c = sampled[i + 1]
        ang = angle(a, b, c)
        if 30 < ang < 140:
            sharp_corners.append(b) # Armazena o ponto do canto

    corners = len(sharp_corners)
    
    if not (1 <= corners <= 3):
        return False

    # 6. Verificação de Agrupamento de Cantos (evita 'Z')
    if corners > 1:
        c_xs = [p[0] for p in sharp_corners]
        c_ys = [p[1] for p in sharp_corners]
        corner_w = max(c_xs) - min(c_xs)
        corner_h = max(c_ys) - min(c_ys)
        corner_diag = math.hypot(corner_w, corner_h) 
        if corner_diag > diag * 0.40:
            return False

    # 7. NOVO: Verificação da Posição Vertical do Canto
    # O(s) canto(s) deve(m) estar no topo do desenho.
    c_ys = [p[1] for p in sharp_corners]
    avg_corner_y = sum(c_ys) / len(c_ys)
    
    # Normaliza a posição y (0.0 = topo, 1.0 = fundo)
    norm_corner_y = (avg_corner_y - miny) / h
    
    # Se o canto estiver na metade inferior (y > 0.4), não é um '^'.
    if norm_corner_y > 0.4:
        return False

    # 8. Verificação de Proporção
    if w == 0:
        return False
    ar = max(w, h) / min(w, h)
    if ar > 3.0: 
        return False

    return True

def recognize_l(points):
    """Detecta 'L' (ou 'L' rotacionado) verificando 1 canto de ~90 graus em uma borda."""
    
    # 1. Pré-processamento e Bounding Box
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
    
    # 'L' deve ter largura e altura
    if diag == 0 or w == 0 or h == 0:
        return False

    # 2. Verificação de Forma Aberta
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    # A distância final deve ser significante, pois é uma forma aberta
    if end_dist < diag * 0.4: 
        return False

    # 3. Reamostragem
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]
    if len(sampled) < 3:
         return False

    # 4. Helper de Ângulo
    def angle(a, b, c):
        bax = a[0] - b[0]
        bay = a[1] - b[1]
        bcx = c[0] - b[0]
        bcy = c[1] - b[1]
        da = math.hypot(bax, bay)
        db = math.hypot(bcx, bcy)
        if da == 0 or db == 0: return 0.0
        dot = max(-1.0, min(1.0, (bax * bcx + bay * bcy) / (da * db)))
        return math.degrees(math.acos(dot))

    # 5. Contagem de Cantos (Procurando por um Ângulo Reto)
    sharp_corners = []
    for i in range(1, len(sampled) - 1):
        a = sampled[i - 1]
        b = sampled[i]
        c = sampled[i + 1]
        ang = angle(a, b, c)
        # Um 'L' tem um ângulo mais fechado (perto de 90) que um 'V'
        if 60 < ang < 120:
            sharp_corners.append(b) 

    corners = len(sharp_corners)
    
    # Permitimos 1 ou 2 cantos (para ruído), mas eles devem estar agrupados
    if not (1 <= corners <= 3):
        return False

    # 6. Verificação de Agrupamento de Cantos (evita 'Z')
    if corners > 1:
        c_xs = [p[0] for p in sharp_corners]
        c_ys = [p[1] for p in sharp_corners]
        corner_w = max(c_xs) - min(c_xs)
        corner_h = max(c_ys) - min(c_ys)
        corner_diag = math.hypot(corner_w, corner_h) 
        if corner_diag > diag * 0.40:
            return False

    # 7. NOVO: Verificação da Posição do Canto (Oposto de 'V')
    c_xs = [p[0] for p in sharp_corners]
    c_ys = [p[1] for p in sharp_corners]
    avg_corner_x = sum(c_xs) / len(c_xs)
    avg_corner_y = sum(c_ys) / len(c_ys)

    norm_corner_x = (avg_corner_x - minx) / w
    norm_corner_y = (avg_corner_y - miny) / h
    
    # O canto deve estar em uma das 4 BORDAS (x < 0.3 ou x > 0.7 OU y < 0.3 ou y > 0.7)
    is_on_edge_x = norm_corner_x < 0.3 or norm_corner_x > 0.7
    is_on_edge_y = norm_corner_y < 0.3 or norm_corner_y > 0.7
    
    # Se o canto estiver no "meio" (como um 'V' ou 'Caret'), rejeita.
    if not is_on_edge_x and not is_on_edge_y:
        return False

    # 8. Verificação de Proporção
    # 'L' não deve ser muito achatado ou fino (diferente de uma linha)
    ar = max(w, h) / min(w, h)
    if ar > 4.0: # Permite um L 'alto' ou 'largo', mas não extremo
        return False

    return True

def recognize_horizontal_line(points):
    """Detecta um traço similar a uma linha horizontal ('-')."""
    
    # 1. Pré-processamento
    # Uma linha pode ser desenhada rapidamente, então 5 pontos é um mínimo razoável.
    if not points or len(points) < 5:
        return False

    pts = [(float(x), float(y)) for x, y in points]

    # 2. Bounding Box (BB)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = maxx - minx
    h = maxy - miny
    diag = math.hypot(w, h)
    
    # Se for um ponto ou uma linha reta sem dimensão
    if diag == 0:
        return False
    
    # 3. Verificação Geométrica Principal (Horizontalidade)
    # A linha deve ser primariamente horizontal.
    
    # Se não tiver largura, não pode ser horizontal.
    if w == 0:
        return False
            
    # A altura (h) deve ser uma pequena fração da largura (w).
    # Se h for mais que 30% de w, não é mais uma "linha horizontal",
    # é um retângulo fino ou uma linha inclinada.
    if h > w * 0.30:
        return False

    # 4. Verificação de Ponto Inicial/Final
    # A distância entre o início e o fim deve ser grande,
    # quase tão grande quanto a largura total. Isso rejeita loops (círculos/quadrados)
    # e também traços que voltam (como um 'Z' achatado).
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    
    # Se a distância de ponta a ponta for menor que 85% da largura,
    # o usuário pode ter voltado, feito uma curva ou um 'Z'.
    if end_dist < w * 0.85:
        return False

    # 5. Verificação de "Retidão" (Contagem de Cantos)
    # Uma linha reta (mesmo mal desenhada) não deve ter cantos.
    
    # Reamostragem
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]
    
    # Se for muito curto para ter 3 pontos de amostra, mas passou nos testes
    # de proporção e distância, é uma linha reta curta.
    if len(sampled) < 3:
        return True 

    # Helper de Ângulo (copiado das outras funções)
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
        # Usamos o mesmo intervalo de "canto" do 'Z' (30-150 graus)
        if 30 < ang < 150:
            corners += 1

    # 6. Verificação Final
    # Permitimos no máximo 1 canto para um leve "tremido" na mão.
    # 2 ou mais cantos indicam um 'Z', 'V', 'N', etc.
    if corners > 1:
        return False

    # Se passou em todas as verificações, é uma linha horizontal.
    return True

def recognize_vertical_line(points):
    """Detecta um traço similar a uma linha vertical ('|')."""
    
    # 1. Pré-processamento
    if not points or len(points) < 5:
        return False

    pts = [(float(x), float(y)) for x, y in points]

    # 2. Bounding Box (BB)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    w = maxx - minx
    h = maxy - miny
    diag = math.hypot(w, h)
    
    if diag == 0:
        return False
    
    # 3. Verificação Geométrica Principal (Verticalidade)
    # A linha deve ser primariamente vertical.
    
    # Se não tiver altura, não pode ser vertical.
    if h == 0:
        return False
            
    # A largura (w) deve ser uma pequena fração da altura (h).
    # Se w for mais que 30% de h, não é mais uma "linha vertical",
    # é um retângulo fino ou uma linha inclinada.
    if w > h * 0.30:
        return False

    # 4. Verificação de Ponto Inicial/Final
    # A distância entre o início e o fim deve ser grande,
    # quase tão grande quanto a altura total.
    sx, sy = pts[0]
    ex, ey = pts[-1]
    end_dist = math.hypot(ex - sx, ey - sy)
    
    # Se a distância de ponta a ponta for menor que 85% da *altura*,
    # o usuário pode ter voltado ou feito uma curva.
    if end_dist < h * 0.85:
        return False

    # 5. Verificação de "Retidão" (Contagem de Cantos)
    # Esta lógica é idêntica à da linha horizontal.
    
    sample_count = min(100, len(pts))
    step = max(1, len(pts) // sample_count)
    sampled = pts[::step]
    
    if len(sampled) < 3:
        return True 

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

    # 6. Verificação Final
    # Permitimos no máximo 1 canto para um leve "tremido" na mão.
    if corners > 1:
        return False

    # Se passou em todas as verificações, é uma linha vertical.
    return True
