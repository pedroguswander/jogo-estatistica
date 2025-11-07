import pygame
import math
import stats_collector
from constants import *


chart1_rect = pygame.Rect(CHARTS_START_X, CHART_ROW_ONE_Y, CHART_WIDTH, CHART_HEIGHT)


def draw_chart_one_border(win):
    border_color = (255, 255, 0)  # Amarelo
    border_thickness = 2
    pygame.draw.rect(win, border_color, chart1_rect, border_thickness)


def draw_chart_one(win, font):
    """Draw an empirical histogram of X (number of enemies defeated before loss)
    and overlay the ideal geometric PMF (support k=0,1,2,...).

    The drawing is constrained to `chart1_rect` so it doesn't overwrite the game area.
    """
    # background for chart area
    pygame.draw.rect(win, (10, 10, 10), chart1_rect)

    # small inner margin
    margin = 12
    left = chart1_rect.x + margin
    top = chart1_rect.y + margin
    right = chart1_rect.x + chart1_rect.width - margin
    bottom = chart1_rect.y + chart1_rect.height - margin

    plot_w = right - left
    plot_h = bottom - top

    # title
    title = "Distribuição Geométrica (X = inimigos abatidos até perder)"
    title_surf = font.render(title, True, (220, 220, 220))
    win.blit(title_surf, (left, top - title_surf.get_height() - 4))

    # get data
    runs = stats_collector.get_runs()
    total = len(runs)
    counts = stats_collector.get_counts()

    if total == 0:
        info = font.render("Sem dados ainda — jogue para gerar runs", True, (180, 180, 180))
        win.blit(info, (left + 6, top + plot_h // 2 - info.get_height() // 2))
        # border
        pygame.draw.rect(win, (100, 100, 100), chart1_rect, 1)
        return

    # Determine x-range to display (include 0 if present)
    min_k = 0 if 0 in counts else 1
    max_k = max(counts.keys()) if counts else min_k
    # show a few extra bins so the PMF tail is visible
    max_k = max(max_k, min_k + 6)

    xs = list(range(min_k, max_k + 1))

    emp = [counts.get(k, 0) / total for k in xs]

    mean = stats_collector.get_mean() or 0.0
    # For geometric defined as #failures before first success: mean = (1-p)/p => p = 1/(mean+1)
    p_hat = 1.0 / (mean + 1.0) if mean >= 0 else 0.0
    pmf = [p_hat * ((1 - p_hat) ** k) if p_hat > 0 else 0.0 for k in xs]

    # scale
    max_val = max(max(emp) if emp else 0.0, max(pmf) if pmf else 0.0, 1e-6)

    # draw grid lines and y labels (4 horizontal grid lines)
    for i in range(5):
        gy = bottom - int(plot_h * i / 4)
        pygame.draw.line(win, (40, 40, 40), (left, gy), (right, gy), 1)
        val = max_val * i / 4
        lbl = font.render(f"{val:.2f}", True, (140, 140, 140))
        win.blit(lbl, (chart1_rect.x + 4, gy - lbl.get_height() // 2))

    # Bars for empirical probabilities
    n = len(xs)
    if n == 0:
        return
    slot = plot_w / n
    bar_w = max(4, int(slot * 0.7))
    for idx, k in enumerate(xs):
        bx = int(left + idx * slot + (slot - bar_w) / 2)
        bh = int((emp[idx] / max_val) * plot_h) if max_val > 0 else 0
        by = bottom - bh
        pygame.draw.rect(win, (50, 130, 200), (bx, by, bar_w, bh))
        # x label (small)
        lbl = font.render(str(k), True, (200, 200, 200))
        lbl_x = int(left + idx * slot + slot / 2 - lbl.get_width() / 2)
        win.blit(lbl, (lbl_x, bottom + 2))

    # PMF overlay (points and connecting line)
    points = []
    for idx, val in enumerate(pmf):
        xpix = int(left + idx * slot + slot / 2)
        ypix = bottom - int((val / max_val) * plot_h) if max_val > 0 else bottom
        points.append((xpix, ypix))
        pygame.draw.circle(win, (255, 200, 0), (xpix, ypix), 3)
    if len(points) > 1:
        pygame.draw.lines(win, (255, 200, 0), False, points, 2)

    # footer info
    info = font.render(f"Runs: {total}   mean={mean:.2f}   p̂={p_hat:.3f}", True, (200, 200, 200))
    win.blit(info, (left + 4, chart1_rect.y + chart1_rect.height - info.get_height() - 6))

    # outer border
    pygame.draw.rect(win, (100, 100, 100), chart1_rect, 1)


