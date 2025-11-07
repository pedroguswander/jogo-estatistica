import pygame
import score
from recognizer import recognize_pattern, identify_pattern
import stats_collector
from enemy import Enemy
from constants import WINDOW_GAME_WIDTH, WINDOW_GAME_HEIGHT


class InputHandler:
    """Handles mouse input for continuous drawing with left mouse button.

    - While left button held: append points.
    - On release: return the finished stroke (list of points) and clear internal buffer.
    """

    def __init__(self):
        self.points = []
        self.is_drawing = False

    def handle_event(self, event):
        # Returns finished stroke (list of points) when left button released, otherwise None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.is_drawing = True
            self.points = [event.pos]
        elif event.type == pygame.MOUSEMOTION and self.is_drawing:
            self.points.append(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_drawing = False
            finished = self.points[:]
            self.points = []
            return finished
        return None

    def draw(self, surface):
        if len(self.points) > 1:
            pygame.draw.lines(surface, (0, 255, 0), False, self.points, 3)

class Game:

    def __init__(self):
        self.window = (WINDOW_GAME_WIDTH, WINDOW_GAME_HEIGHT)
        self.screen = None
        self.font = None
        self.clock = None
        self.input = InputHandler()
        # targets cycle through these patterns
        self.targets = ["square", "z", "circle", "v"]
        self.target_index = 0
        self.fps = 60
        # enemy spawning and management
        self.enemies = []
        self.spawn_timer = 0
        self.spawn_interval = 2.0  # spawn every 2 seconds
        # dead line: choose near the end of the screen
        self.dead_line = pygame.Vector2(self.window[0] - 15, self.window[1] - 15)
        self.recognized = False
        self.delta_time = 0
        self.kill_strike = 0
        self.kill_strike_time = 1000
        self.kill_strike_time_init = 0
        self.enemy_weakness_offset_x = 8

    def start(self):
        score.init_score(0)

        if self.screen is None:
            raise RuntimeError("Game.start() requires `screen` to be set by StateManager before calling.")
        if self.clock is None:
            # fallback: create a local clock if not provided
            self.clock = pygame.time.Clock()

        # spawn first enemy
        self.enemies.append(Enemy.spawn(self.window[0]))
        self.request_quit = False

    def update(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # request the StateManager to stop the main loop
                self.request_quit = True
                return

            # let input handler process event; if it returns a finished stroke, check pattern
            finished = self.input.handle_event(event)
            if finished is not None:
                # identify which pattern (if any) the player drew
                matched, pattern = identify_pattern(finished)
                self.recognized = matched
                if matched:
                    print(f"Pattern recognized: {pattern}")
                    # try to destroy enemies under the stroke that have this weakness
                    destroyed = self.handle_recognized_pattern(pattern)
                    self.handle_kill_enemy(destroyed)
                # advance target only when recognized (keeps current behavior)

        self.delta_time = self.clock.tick(self.fps) / 1000.0  # convert to seconds

        self.spawn_new_enemies()

        self.check_game_over()


    def handle_kill_enemy(self, destroyed):
        if destroyed > 0:
            # increment score by number destroyed
            score.increment_score(destroyed)
            self.kill_strike = destroyed
            self.kill_strike_time_init = pygame.time.get_ticks()

    def spawn_new_enemies(self):
        self.spawn_timer += self.delta_time
        if self.spawn_timer >= self.spawn_interval:
            self.enemies.append(Enemy.spawn(self.window[0]))
            self.spawn_timer = 0

    def check_balloon_destroyed(self):
        # deprecated: handling is done in handle_recognized_pattern
        return

    def check_game_over(self):
        # Game over if any non-defeated enemy reaches bottom of screen
        for enemy in self.enemies:
            if enemy.rect.bottom >= self.dead_line.y:
                if enemy.is_defeated:
                    # Mark defeated enemies as inactive when they reach the deadline
                    enemy.dead_line_reached = True
                else:
                    # Only trigger game over for non-defeated enemies
                    # Record empirical run: number of enemies defeated until the loss
                    defeated_count = sum(1 for e in self.enemies if getattr(e, 'is_defeated', False))
                    try:
                        stats_collector.record_run(defeated_count)
                    except Exception:
                        # don't crash the game if stats collector fails
                        pass
                    self.request_state_change = "GAME_OVER"
                    return True
        return False

    def handle_recognized_pattern(self, pattern):
        if not pattern:
            return 0

        destroyed = 0
        for enemy in self.enemies:
            if not enemy.active or enemy.is_defeated:
                continue
            if pattern in enemy.weakness:
                enemy.weakness.remove(pattern)

            if len(enemy.weakness) == 0:
                enemy.defeat()  # Start defeat animation
                destroyed += 1
            else:
                continue

        return destroyed

    def draw(self):
        self.screen.fill((0, 0, 0))
        # draw current stroke (while player holds left mouse)
        self.input.draw(self.screen)
        
        # draw score / counter
        text = self.font.render(f"Acertos: {score.get_score()}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        self.enemies = [enemy for enemy in self.enemies if enemy.active]
        for enemy in self.enemies:
            enemy.update(self.delta_time)
            enemy.draw(self.screen)
            # draw enemy weakness symbol above the enemy
            enemy.draw_enemy_weakness(self.screen)

        pygame.draw.line(self.screen, (255, 0, 0), (0, self.dead_line.y), (self.window[0], self.dead_line.y), 2)

        self.draw_kill_strike()

        self.draw_game_border()


    def draw_kill_strike(self):
        text_string = ""
        actual_time = pygame.time.get_ticks()

        if self.kill_strike <= 1:
            return

        if self.kill_strike == 2:
            text_string = "2 x COMBO"
        elif self.kill_strike == 3: 
            text_string = "3 x COMBO"

        if text_string != "" and  actual_time - self.kill_strike_time_init < self.kill_strike_time:
            texto_surface = self.font.render(text_string, True, (255, 255, 0)) # Amarelo, por exemplo

            # Cria o Retângulo (Rect) e o centraliza na posição desejada
            # (360, 640) parece ser a posição no seu jogo, vou assumir.
            texto_rect = texto_surface.get_rect(center=(self.window[0]/2, self.window[1]/2))

            # Desenha o texto na tela
            self.screen.blit(texto_surface, texto_rect)

    def draw_game_border(self):
        """Desenha um retângulo de 360x720 centralizado na tela (1920x1080)
        para indicar a área de jogo."""
        
        # A cor da borda (por exemplo, azul neon)
        border_color = (0, 150, 255)  # RGB para um azul claro/ciano
        border_thickness = 4  # Espessura da borda

        game_area_x = (self.window[0] - WINDOW_GAME_WIDTH) // 2
        game_area_y = (self.window[1] -  WINDOW_GAME_HEIGHT) // 2

        # Cria o objeto Rect para a borda
        # Posição (x, y) e Dimensões (largura, altura)
        border_rect = pygame.Rect(
            game_area_x, 
            game_area_y, 
            WINDOW_GAME_WIDTH, 
            WINDOW_GAME_HEIGHT
        )
        
        # Desenha o retângulo na superfície da tela. O último parâmetro (thickness)
        # desenha apenas o contorno (borda) em vez de um retângulo sólido.
        pygame.draw.rect(self.screen, border_color, border_rect, border_thickness)
            

        
        
