import pygame
import math
import stats_collector


class StatsScreen:
    """Pygame state that displays an empirical histogram of X and overlays a
    fitted geometric PMF.

    Controls:
    - ENTER or ESC: return to main menu
    - R: reset collected runs
    """

    def __init__(self):
        self.screen = None
        self.font = None
        self.clock = None
        self.window = None

    def start(self):
        if self.screen is None or self.font is None:
            raise RuntimeError("StatsScreen.start() requires screen and font to be set by StateManager")

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.request_quit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    self.request_state_change = "MAIN_MENU"
                elif event.key == pygame.K_r:
                    stats_collector.reset()

    def draw(self):
        self.screen.fill((0, 0, 0))

        runs = stats_collector.get_runs()
        total = len(runs)
        w, h = self.window

        header = self.font.render("Estatísticas - Distribuição Geométrica (X = inimigos abatidos até perder)", True, (255, 255, 255))
        self.screen.blit(header, (20, 10))

        if total == 0:
            info = self.font.render("Nenhum dado ainda. Jogue para gerar runs. Pressione 'R' para reset.", True, (200, 200, 200))
            self.screen.blit(info, (20, 50))
            footer = self.font.render("ENTER: menu", True, (180, 180, 180))
            self.screen.blit(footer, (20, h - 40))
            pygame.display.flip()
            return

        counts = stats_collector.get_counts()
        max_k = max(counts.keys()) if counts else 1
        xs = list(range(1, max_k + 1))
        emp = [counts.get(k, 0) / total for k in xs]

        mean = stats_collector.get_mean() or 0.0
        p_hat = 1.0 / mean if mean > 0 else 0.0
        pmf = [p_hat * ((1 - p_hat) ** (k - 1)) if p_hat > 0 else 0.0 for k in xs]

        # Plot area
        margin = 80
        plot_w = w - 2 * margin
        plot_h = h - 2 * margin
        origin_x = margin
        origin_y = h - margin

        max_val = max(max(emp) if emp else 0.0, max(pmf) if pmf else 0.0, 1e-6)

        # Draw horizontal grid and y labels
        for i in range(5):
            y = origin_y - int(plot_h * i / 4)
            pygame.draw.line(self.screen, (40, 40, 40), (origin_x, y), (origin_x + plot_w, y), 1)
            val = max_val * i / 4
            lbl = self.font.render(f"{val:.2f}", True, (140, 140, 140))
            self.screen.blit(lbl, (5, y - lbl.get_height() // 2))

        # Bars for empirical probabilities
        bar_slot = plot_w / len(xs)
        bar_w = max(4, int(bar_slot * 0.7))
        for idx, k in enumerate(xs):
            bx = origin_x + int(idx * bar_slot) + int((bar_slot - bar_w) / 2)
            bh = int((emp[idx] / max_val) * plot_h) if max_val > 0 else 0
            by = origin_y - bh
            pygame.draw.rect(self.screen, (50, 130, 200), (bx, by, bar_w, bh))
            # x label
            lbl = self.font.render(str(k), True, (200, 200, 200))
            lbl_x = origin_x + int(idx * bar_slot) + int(bar_slot / 2) - lbl.get_width() // 2
            self.screen.blit(lbl, (lbl_x, origin_y + 4))

        # PMF overlay (draw points and connect)
        points = []
        for idx, val in enumerate(pmf):
            xpix = origin_x + int(idx * bar_slot + bar_slot / 2)
            ypix = origin_y - int((val / max_val) * plot_h) if max_val > 0 else origin_y
            points.append((xpix, ypix))
            pygame.draw.circle(self.screen, (255, 200, 0), (xpix, ypix), 4)
        if len(points) > 1:
            pygame.draw.lines(self.screen, (255, 200, 0), False, points, 2)

        # Info
        info = self.font.render(f"Runs: {total}   mean X={mean:.2f}   p_hat={p_hat:.3f}   (R=reset, ENTER=menu)", True, (220, 220, 220))
        self.screen.blit(info, (margin, 20))

        pygame.display.flip()
