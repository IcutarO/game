import pygame
import random
import sqlite3
import time

class Player:
    def __init__(self, name):
        self.name = name
        self.x = 300
        self.y = 200
        self.score = 0

    def increase_score(self):
        self.score += 1

class Square:
    def __init__(self):
        self.x = random.randint(0, 575)
        self.y = random.randint(0, 375)
        self.color = (255, 0, 0)
        self.width = 25
        self.height = 25
        self.creation_time = time.time()

    def should_remove(self):
        return time.time() - self.creation_time >= 5

class Game:
    def __init__(self):
        pygame.init()
        self.W, self.H = 600, 400
        self.is_game = False
        self.is_game_over = False
        self.dsp = pygame.display
        self.win = self.dsp.set_mode((self.W, self.H))
        self.clock = pygame.time.Clock()
        self.player = None
        self.squares = []
        self.load_top_players()
        self.game_time = 20
        self.start_time = None
        self.font = pygame.font.Font(None, 36)

    def run(self):
        while True:
            if not self.is_game:
                self.get_player_name()
                self.is_game = True
                self.is_game_over = False
                self.player.score = 0
                self.start_time = time.time()
                self.squares = []
            self.game_loop()
            if not self.is_game_over:
                self.save_score()
                self.display_top_players()
                self.display_buttons()
            else:
                self.display_game_over_buttons()
                self.display_top_players_terminal()
                return
            pygame.quit()

    def game_loop(self):
        while self.is_game and not self.is_game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_game = False
            self.handle_input()
            self.update_display()
            self.create_squares()
            self.check_collisions()
            self.remove_old_squares()
            self.clock.tick(100)
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.game_time:
                self.is_game_over = True

    def get_player_name(self):
        input_box = pygame.Rect(150, 100, 300, 32)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = 'Введите никнейм'
        while not self.is_game:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box.collidepoint(event.pos):
                        active = not active
                        if text == 'Введите никнейм':
                            text = ''
                    else:
                        active = False
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            if text:
                                self.player = Player(text)
                                return
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
            self.win.fill((0, 0, 0))
            txt_surface = self.font.render(text, True, color)
            width = max(400, txt_surface.get_width() + 10)
            input_box.w = width
            self.win.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(self.win, color, input_box, 2)
            pygame.display.flip()
            self.clock.tick(30)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.player.y -= 2
        if keys[pygame.K_DOWN]:
            self.player.y += 2
        if keys[pygame.K_LEFT]:
            self.player.x -= 2
        if keys[pygame.K_RIGHT]:
            self.player.x += 2

    def update_display(self):
        self.win.fill((0, 0, 0))
        for square in self.squares:
            pygame.draw.rect(self.win, square.color, (square.x, square.y, square.width, square.height))
        pygame.draw.circle(self.win, (204, 0, 204), (self.player.x, self.player.y), 25)

        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        self.win.blit(score_text, (10, 10))

        elapsed_time = int(self.game_time - (time.time() - self.start_time))
        timer_text = self.font.render(f"Time: {elapsed_time} s", True, (255, 255, 255))
        self.win.blit(timer_text, (self.W - 200, 10))

        pygame.display.update()

    def create_squares(self):
        if len(self.squares) < 5:
            self.squares.append(Square())

    def check_collisions(self):
        for square in self.squares:
            if (self.player.x - 25 <= square.x <= self.player.x + 25 and
                self.player.y - 25 <= square.y <= self.player.y + 25):
                self.player.increase_score()
                self.squares.remove(square)

    def remove_old_squares(self):
        self.squares = [square for square in self.squares if not square.should_remove()]

    def load_top_players(self):
        self.conn = sqlite3.connect("top_players.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS top_players (name TEXT, score INT)")
        self.conn.commit()

    def display_top_players(self):
        top_players = self.get_top_players()
        y_offset = 100
        title_text = self.font.render("Топ-5 игроков:", True, (255, 255, 255))
        self.win.blit(title_text, (self.W // 2 - title_text.get_width() // 2, 50 + y_offset))
        for i, (name, score) in enumerate(top_players):
            text = f"{i + 1}. {name}: {score}"
            player_text = self.font.render(text, True, (255, 255, 255))
            self.win.blit(player_text, (self.W // 2 - player_text.get_width() // 2, 100 + y_offset))
            y_offset += 40

    def get_top_players(self):
        self.cursor.execute("SELECT * FROM top_players ORDER BY score DESC LIMIT 5")
        top_players = self.cursor.fetchall()
        return top_players

    def display_buttons(self):
        restart_button = pygame.Rect(200, 300, 200, 50)
        end_button = pygame.Rect(200, 360, 200, 50)

        pygame.draw.rect(self.win, (0, 255, 0), restart_button)
        pygame.draw.rect(self.win, (255, 0, 0), end_button)

        restart_text = self.font.render("Начать заново", True, (0, 0, 0))
        end_text = self.font.render("Закончить игру", True, (0, 0, 0))

        self.win.blit(restart_text, (240, 315))
        self.win.blit(end_text, (240, 375))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        return
                    if end_button.collidepoint(event.pos):
                        pygame.quit()
                        return

    def display_game_over_buttons(self):
        restart_button = pygame.Rect(200, 300, 200, 50)
        end_button = pygame.Rect(200, 360, 200, 50)

        pygame.draw.rect(self.win, (0, 255, 0), restart_button)
        pygame.draw.rect(self.win, (255, 0, 0), end_button)

        restart_text = self.font.render("Начать заново", True, (0, 0, 0))
        end_text = self.font.render("Закончить игру", True, (0, 0, 0))

        self.win.blit(restart_text, (240, 315))
        self.win.blit(end_text, (240, 375))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.collidepoint(event.pos):
                        return
                    if end_button.collidepoint(event.pos):
                        pygame.quit()
                        return

    def display_top_players_terminal(self):
        top_players = self.get_top_players()
        print("Топ-5 игроков:")
        for i, (name, score) in enumerate(top_players):
            print(f"{i + 1}. {name}: {score}")

game = Game()
game.run()
