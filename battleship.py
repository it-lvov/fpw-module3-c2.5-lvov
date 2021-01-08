from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # метод, проверяющий равенство точек
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    # метод, отвечающий за вывод в консоль
    def __repr__(self):
        return f"({self.x}, {self.y})"

############################################################
# ИСКЛЮЧЕНИЯ

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Выстрел в молоко (за доску)"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Выстрел в ту же воронку (уже стреляли сюда)"

class BoardWrongShipException(BoardException):
    pass

############################################################

class Ship:


    def __init__(self, bow, l, o):  #0-vertical 1-horizontal
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []


        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y


            if self.o == 0:
                cur_x += i
            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:

    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid

        # счетчик сколько кораблей уничтожено
        self.count = 0

        # доска двумерным списком
        self.field = [["O"] * size for _ in range(size)]

        # список занятых точек
        self.busy = []

        # список кораблей на доске
        self.ships = []

    # постановка корабля на доску
    def add_ship(self, ship):

        # проверка, что корабль в пределах доски и что он не назанятых точках
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()

        for d in ship.dots:
            self.field[d.x][d.y] = "∎" # "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # контур корабля
    def contour(self, ship, verb = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        # распаковка
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                # проверка что точка в пределах доски и вне списка занятых полей
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "•"
                    self.busy.append(cur)

    # печать доски
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"

        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        # замена для доски компьютера
        if self.hid:
            res = res.replace("∎", "O")
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # выстрелы
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print('Убил!')
                    return False
                else:
                    print('Ранил!')
                    return True

        self.field[d.x][d.y] = "•"
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"и его ход: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите координаты в формате а1: ")
                continue

            x, y = cords


            if not (x.isdigit()) or not (y.isdigit()):
                print("Введите числа! ") # Введите координаты в формате а1 (русская буква и число
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)



class Game:

    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    # случайная расстановка кораблей
    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None

                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("*" * 50)
        print("  Игра МОРСКОЙ БОЙ")
        print("*" * 50)
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска человека:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("+" * 40)
                print("Ходит человек...")
                repeat = self.us.move()
            else:
                print("+" * 40)
                print("Ходит компьютер...")
                repeat = self.ai.move()
            if repeat:
               num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Человек выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

#####################################

g = Game()
g.start()