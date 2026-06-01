# models.py - Съдържа всички класове (обекти) за играта Pac-Man.

import random

class PacManGame: #Главен клас на играта. Съдържа логиката за движение, точки, духове и лабиринта

    # ------Символи за лабиринта
    WALL = "#"
    DOT = "."
    POWER = "O"
    EMPTY = " "
    PACMAN = "P"
    GHOSTS = "G"

    def __init__(self, width=19, height=21): # ---Конструктор (self метод) - инициализира играта
        self.width = width
        self.height = height
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.won = False

        self.pacman_x = 9 # ----Позиция на Pac-Man
        self.pacman_y = 15

        self.ghosts = [         # ------Духове
            {"x": 9, "y": 9, "name": "Blinky", "color": "red", "dx": 1, "dy": 0},
            {"x": 8, "y": 9, "name": "Pinky", "color": "pink", "dx": -1, "dy": 0},
            {"x": 10, "y": 9, "name": "Inky", "color": "cyan", "dx": 0, "dy": 1},
            {"x": 9, "y": 10, "name": "Clyde", "color": "orange", "dx": 0, "dy": -1},
        ]

        self.power_mode = False
        self.power_timer = 0

        self.maze = self._create_maze()     # ----Генериране на лабиринта
        self.total_dots = self._count_dots()

    def _create_maze(self): # Създава матрица (2D списък) с лабиринта.
        layout = [
            "###################",
            "#........#........#",
            "#.##.###.#.###.##.#",
            "#O##.###.#.###.##O#",
            "#.##.###.#.###.##.#",
            "#.................#",
            "#.##.#.##.##.#.##.#",
            "#.##.#.##.##.#.##.#",
            "#....#.......#....#",
            "####.###   ###.####",
            "O.....       .....O",
            "####..##GGG##..####",
            "####.  #GGG#  .####",
            "#....#       #....#",
            "#.##.#########.##.#",
            "#........#........#",
            "#.##.###.#.###.##.#",
            "#O...............O#",
            "###.#.#.###.#.#.###",
            "#......#.P.#......#",
            "###################",
        ]
        maze = []
        for row in layout:
            padded = row.ljust(self.width)[:self.width]
            maze.append(list(padded))
        return maze

    def _count_dots(self): # --Метод, който брои всички точки (. и O) в лабиринта.
        count = 0
        for row in self.maze:
            for cell in row:
                if cell in (self.DOT, self.POWER):
                    count += 1
        return count

    def move_pacman(self, dx, dy): # Премества Pac-Man в посока (dx, dy). Проверява за стени, точки, power-up и духове.
        new_x = self.pacman_x + dx
        new_y = self.pacman_y + dy

        if not (0 <= new_x < self.width and 0 <= new_y < self.height): # Проверява за граници и стени
            return False
        if self.maze[new_y][new_x] == self.WALL:
            return False

        self.pacman_x = new_x   # ---Премества Pac-Man
        self.pacman_y = new_y

        cell = self.maze[new_y][new_x]  # ---Отчита и добавя точките в резултатът
        if cell == self.DOT:
            self.score += 10
            self.maze[new_y][new_x] = self.EMPTY
            self.total_dots -= 1
        elif cell == self.POWER:
            self.score += 50
            self.maze[new_y][new_x] = self.EMPTY
            self.total_dots -= 1
            self.power_mode = True
            self.power_timer = 30

        if self.total_dots <= 0: # ---Проверка за победа
            self.won = True
            self.game_over = True

        self._check_ghost_collision()  # ---Проверка за сблъсък с дух
        return True
    def move_ghosts(self): # ---Премества всички духове с основна AI логика
        for ghost in self.ghosts:
            if self.power_mode:     # ---Намалява "power timer"
                self.power_timer -= 1
                if self.power_timer <= 0:
                    self.power_mode = False

            new_x = ghost["x"] + ghost["dx"] # --Движение в права посока, докато не се удари в стена
            new_y = ghost["y"] + ghost["dy"]

            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)] # --Ако има стена – избира случайна посока
            if (not (0 <= new_x < self.width and 0 <= new_y < self.height)
                    or self.maze[new_y][new_x] == self.WALL):
                random.shuffle(directions)
                for dx, dy in directions:
                    nx, ny = ghost["x"] + dx, ghost["y"] + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height
                            and self.maze[ny][nx] != self.WALL):
                        ghost["dx"], ghost["dy"] = dx, dy
                        ghost["x"], ghost["y"] = nx, ny
                        break
            else:
                ghost["x"] = new_x
                ghost["y"] = new_y

        self._check_ghost_collision()

    def _check_ghost_collision(self): # Проверява дали Pac-Man е хванат от дух.
        # Ако PacMan е в power mode - духът се respawn-ва. || Ако не е - PacMan губи живот.
        for ghost in self.ghosts:
            if ghost["x"] == self.pacman_x and ghost["y"] == self.pacman_y:
                if self.power_mode:    # --Respawn-ва духа обратно в центъра
                    ghost["x"] = 9
                    ghost["y"] = 9
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        self.pacman_x = 9 # --Respawn-ва Pac-Man
                        self.pacman_y = 15

    def get_sorted_scores(self, scores_list): # --Приема списък от речници и ги сортира низходящо по ключ "score".
        sorted_scores = sorted(scores_list, key=lambda x: x["score"], reverse=True)
        return sorted_scores

    def get_status(self):   # --Връща речник с текущото състояние на играта
        return {
            "score": self.score,
            "lives": self.lives,
            "level": self.level,
            "game_over": self.game_over,
            "won": self.won,
            "power_mode": self.power_mode,
            "pacman_pos": (self.pacman_x, self.pacman_y),
            "dots_remaining": self.total_dots,
        }

    def reset(self):    # ---Нулира играта до началното й състояние
        self.__init__(self.width, self.height)

