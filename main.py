"""
main.py - Стартира играта Pac-Man.
Създава обект от класа PacManGame и се използват неговите методи.
Съдържа: цикли, условни изрази, сортиране.
"""

import pygame
import sys
import os

from models import PacManGame

# ──────────────────────────────────────────────
#  КОНСТАНТИ
# ──────────────────────────────────────────────
CELL = 32  # размер на клетка в пиксели
FPS = 10  # кадри в секунда

# Цветова палитра (ретро аркада)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
BLUE = (33, 33, 222)
RED = (220, 30, 30)
PINK = (255, 180, 200)
CYAN = (0, 220, 220)
ORANGE = (255, 165, 0)
GRAY = (150, 150, 150)
DBLUE = (0, 0, 80)

GHOST_COLORS = {
    "Blinky": RED,
    "Pinky": PINK,
    "Inky": CYAN,
    "Clyde": ORANGE,
}


# ──────────────────────────────────────────────
#  ПОМОЩНИ ФУНКЦИИ ЗА РИСУВАНЕ
# ──────────────────────────────────────────────
def draw_maze(screen, game):
    """Рисува лабиринта клетка по клетка – използва вложен цикъл."""
    for row_idx, row in enumerate(game.maze):  # цикъл по редове
        for col_idx, cell in enumerate(row):  # цикъл по колони
            x = col_idx * CELL
            y = row_idx * CELL

            if cell == game.WALL:
                pygame.draw.rect(screen, BLUE, (x, y, CELL, CELL))
                pygame.draw.rect(screen, DBLUE, (x + 2, y + 2, CELL - 4, CELL - 4))
            elif cell == game.DOT:
                cx, cy = x + CELL // 2, y + CELL // 2
                pygame.draw.circle(screen, WHITE, (cx, cy), 3)
            elif cell == game.POWER:
                cx, cy = x + CELL // 2, y + CELL // 2
                pygame.draw.circle(screen, YELLOW, (cx, cy), 8)


def draw_pacman(screen, game):
    """Рисува Pac-Man като жълт кръг."""
    px = game.pacman_x * CELL + CELL // 2
    py = game.pacman_y * CELL + CELL // 2
    pygame.draw.circle(screen, YELLOW, (px, py), CELL // 2 - 2)


def draw_ghosts(screen, game):
    """
    Рисува духовете – ако е power mode, стават сини.
    Използва условен израз.
    """
    for ghost in game.ghosts:
        gx = ghost["x"] * CELL
        gy = ghost["y"] * CELL
        color = (0, 0, 200) if game.power_mode else GHOST_COLORS[ghost["name"]]

        # Тяло (правоъгълник с заоблен връх)
        body = pygame.Rect(gx + 2, gy + CELL // 3, CELL - 4, CELL - CELL // 3 - 2)
        pygame.draw.rect(screen, color, body)
        pygame.draw.circle(screen, color,
                           (gx + CELL // 2, gy + CELL // 3), (CELL - 4) // 2)

        # Очи (бели с тъмна зеница)
        for ex, ey in [(gx + 9, gy + 10), (gx + 21, gy + 10)]:
            pygame.draw.circle(screen, WHITE, (ex, ey), 4)
            pygame.draw.circle(screen, BLACK, (ex + 1, ey + 1), 2)


def draw_hud(screen, game, font):
    """Рисува резултата, животите и нивото."""
    score_txt = font.render(f"Score: {game.score}", True, WHITE)
    lives_txt = font.render(f"Lives: {game.lives}", True, YELLOW)
    level_txt = font.render(f"Level: {game.level}", True, CYAN)
    screen.blit(score_txt, (10, game.height * CELL + 5))
    screen.blit(lives_txt, (200, game.height * CELL + 5))
    screen.blit(level_txt, (380, game.height * CELL + 5))


def draw_overlay(screen, game, font_big, font_small):
    """Показва съобщение при край на игра или победа – условен израз."""
    if game.game_over:
        if game.won:
            msg = "YOU WIN!"
            color = YELLOW
        else:
            msg = "GAME OVER"
            color = RED

        overlay = pygame.Surface((game.width * CELL, game.height * CELL), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        txt = font_big.render(msg, True, color)
        sub = font_small.render("Press R to restart  |  Q to quit", True, WHITE)
        cx = game.width * CELL // 2

        screen.blit(txt, txt.get_rect(center=(cx, game.height * CELL // 2 - 20)))
        screen.blit(sub, sub.get_rect(center=(cx, game.height * CELL // 2 + 30)))


# ──────────────────────────────────────────────
#  ТАБЛИЦА С РЕЗУЛТАТИ (демонстрира сортиране)
# ──────────────────────────────────────────────
LEADERBOARD = [
    {"name": "Alice", "score": 1500},
    {"name": "Bob", "score": 3200},
    {"name": "Carol", "score": 800},
    {"name": "Dave", "score": 2100},
]


def show_leaderboard(game):
    """
    Добавя резултата на играча, сортира класацията и я отпечатва.
    Демонстрира използването на метода get_sorted_scores() от models.py.
    """
    LEADERBOARD.append({"name": "You", "score": game.score})
    sorted_lb = game.get_sorted_scores(LEADERBOARD)  # ← метод от класа

    print("\n══════════════════════════")
    print("      LEADERBOARD")
    print("══════════════════════════")
    # Цикъл + условен израз за форматиран изход
    for i, entry in enumerate(sorted_lb, start=1):
        marker = " ◄" if entry["name"] == "You" else ""
        print(f"  {i}. {entry['name']:<10} {entry['score']:>6} pts{marker}")
    print("══════════════════════════\n")


# ──────────────────────────────────────────────
#  ГЛАВНА ФУНКЦИЯ
# ──────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("Pac-Man  –  Python курсова работа")

    # ── Създаване на обект от класа (изисквано) ──
    game = PacManGame()

    WIN_W = game.width * CELL
    WIN_H = game.height * CELL + 40  # +40 за HUD

    screen = pygame.display.set_mode((WIN_W, WIN_H))
    clock = pygame.time.Clock()

    font_big = pygame.font.SysFont("consolas", 42, bold=True)
    font_small = pygame.font.SysFont("consolas", 22)
    font_hud = pygame.font.SysFont("consolas", 20)

    ghost_timer = 0  # управлява честотата на движение на духовете

    # ── Главен игрови цикъл ──
    running = True
    while running:

        # ── Обработка на събития ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

                elif event.key == pygame.K_r and game.game_over:
                    show_leaderboard(game)
                    game.reset()  # ← метод от класа

                elif not game.game_over:
                    # Посоки на движение – условни изрази
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        game.move_pacman(-1, 0)  # ← метод от класа
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        game.move_pacman(1, 0)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        game.move_pacman(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game.move_pacman(0, 1)

        # ── Движение на духовете (по-бавно от Pac-Man) ──
        if not game.game_over:
            ghost_timer += 1
            if ghost_timer >= 3:  # духовете се движат всеки 3-ти кадър
                game.move_ghosts()  # ← метод от класа
                ghost_timer = 0

        # ── Рисуване ──
        screen.fill(BLACK)
        draw_maze(screen, game)
        draw_pacman(screen, game)
        draw_ghosts(screen, game)
        draw_hud(screen, game, font_hud)
        draw_overlay(screen, game, font_big, font_small)

        pygame.display.flip()
        clock.tick(FPS)

        # ── Печата статус в конзолата при game over ──
        status = game.get_status()  # ← метод от класа
        if status["game_over"]:
            result = "WON" if status["won"] else "LOST"
            print(f"[STATUS] Game {result} | Score: {status['score']} | Lives: {status['lives']}")

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
