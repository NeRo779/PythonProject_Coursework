"""
models.py - Съдържа всички класове (обекти) за играта Pac-Man.
Спазва изискването: клас с метод self и поне два допълнителни метода.
"""

import random


class PacManGame:
    """
    Главният клас на играта Pac-Man.
    Съдържа логиката за движение, точки, духове и лабиринта.
    """

    # Символи за лабиринта
    WALL = "#"
    DOT = "."
    POWER = "O"
    EMPTY = " "
    PACMAN = "P"
    GHOST = "G"

    def __init__(self, width=19, height=21):
        """
        Конструктор (self метод) - инициализира играта.
        Изисква: метод с self.
        """
        self.width = width
        self.height = height
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.won = False

        # Позиция на Pac-Man
        self.pacman_x = 9
        self.pacman_y = 15

        # Духове
        self.ghosts = [
            {"x": 9, "y": 9, "name": "Blinky", "color": "red", "dx": 1, "dy": 0},
            {"x": 8, "y": 9, "name": "Pinky", "color": "pink", "dx": -1, "dy": 0},
            {"x": 10, "y": 9, "name": "Inky", "color": "cyan", "dx": 0, "dy": 1},
            {"x": 9, "y": 10, "name": "Clyde", "color": "orange", "dx": 0, "dy": -1},
        ]

        self.power_mode = False
        self.power_timer = 0

        # Генерира лабиринта
        self.maze = self._create_maze()
        self.total_dots = self._count_dots()

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 1 – създаване на лабиринта                      #
    # ------------------------------------------------------------------ #
    def _create_maze(self):
        """
        Създава матрица (2D списък) с лабиринта.
        Изисква: допълнителен метод.
        """
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
            # Допълва до нужната ширина
            padded = row.ljust(self.width)[:self.width]
            maze.append(list(padded))
        return maze

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 2 – броене на точките                           #
    # ------------------------------------------------------------------ #
    def _count_dots(self):
        """
        Брои всички точки (. и O) в лабиринта.
        Изисква: допълнителен метод.
        """
        count = 0
        for row in self.maze:
            for cell in row:
                if cell in (self.DOT, self.POWER):
                    count += 1
        return count

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 3 – преместване на Pac-Man                      #
    # ------------------------------------------------------------------ #
    def move_pacman(self, dx, dy):
        """
        Премества Pac-Man в посока (dx, dy).
        Проверява за стени, точки, power-up и духове.
        Изисква: допълнителен метод с логика (цикли и условни изрази).
        """
        new_x = self.pacman_x + dx
        new_y = self.pacman_y + dy

        # Проверка за граници и стени
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return False
        if self.maze[new_y][new_x] == self.WALL:
            return False

        # Премества Pac-Man
        self.pacman_x = new_x
        self.pacman_y = new_y

        # Вземане на точка
        cell = self.maze[new_y][new_x]
        if cell == self.DOT:
            self.score += 10
            self.maze[new_y][new_x] = self.EMPTY
            self.total_dots -= 1
        elif cell == self.POWER:
            self.score += 50
            self.maze[new_y][new_x] = self.EMPTY
            self.total_dots -= 1
            self.power_mode = True
            self.power_timer = 30  # 30 хода power mode

        # Проверка за победа
        if self.total_dots <= 0:
            self.won = True
            self.game_over = True

        # Проверка за сблъсък с дух
        self._check_ghost_collision()
        return True

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 4 – движение на духовете                        #
    # ------------------------------------------------------------------ #
    def move_ghosts(self):
        """
        Премества всички духове с основна AI логика.
        Използва цикли и условни изрази (изисквано).
        """
        for ghost in self.ghosts:
            # Намалява power timer
            if self.power_mode:
                self.power_timer -= 1
                if self.power_timer <= 0:
                    self.power_mode = False

            # Опитва се да се движи в текущата посока
            new_x = ghost["x"] + ghost["dx"]
            new_y = ghost["y"] + ghost["dy"]

            # Ако има стена – избира случайна посока
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
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

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 5 – проверка за сблъсък                        #
    # ------------------------------------------------------------------ #
    def _check_ghost_collision(self):
        """
        Проверява дали Pac-Man е хванат от дух.
        Ако е в power mode – духът се изпраща обратно.
        Иначе губи живот.
        """
        for ghost in self.ghosts:
            if ghost["x"] == self.pacman_x and ghost["y"] == self.pacman_y:
                if self.power_mode:
                    # Изпраща духа обратно в центъра
                    ghost["x"] = 9
                    ghost["y"] = 9
                    self.score += 200
                else:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # Нулира позицията на Pac-Man
                        self.pacman_x = 9
                        self.pacman_y = 15

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 6 – сортиране на резултатите                    #
    # ------------------------------------------------------------------ #
    def get_sorted_scores(self, scores_list):
        """
        Приема списък от речници {'name': str, 'score': int}
        и ги сортира по точки (низходящо).
        Изисква: сортиране (изрично споменато в заданието).
        """
        # Сортира по ключ 'score' в низходящ ред
        sorted_scores = sorted(scores_list, key=lambda x: x["score"], reverse=True)
        return sorted_scores

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 7 – статус на играта                            #
    # ------------------------------------------------------------------ #
    def get_status(self):
        """
        Връща речник с текущото състояние на играта.
        Полезно за визуализация и дебъгване.
        """
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

    # ------------------------------------------------------------------ #
    #  ДОПЪЛНИТЕЛЕН МЕТОД 8 – нулиране на играта                          #
    # ------------------------------------------------------------------ #
    def reset(self):
        """
        Нулира играта до началното й състояние.
        """
        self.__init__(self.width, self.height)

