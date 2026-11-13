import pygame
import time
import json
from characters import Player, Monster, Coin
from arena import Arena
from draw import Draw
from pathlib import Path

class Game:
    def __init__(self):
        pygame.init()

        self.door = pygame.image.load(str(Path(__file__).parent / "assets" / "door.png"))
        self.door_rect = self.door.get_rect(center=(920, 600))

        self.coin = pygame.image.load(str(Path(__file__).parent / "assets" / "coin.png"))

        self.monster = pygame.image.load(str(Path(__file__).parent / "assets" / "monster.png"))
        self.monster_list = []
        self.monster_positions = [
            [6, 5],
            [9, 0],
            [23, 6],
            [13, 12]
        ]

        self.player_spawn = (0, 90)
        self.player = Player(*self.player_spawn)
        self.menu_states = ["playing", "highscores"]
        self.menu_options = ["Play Game", "Highscores"]
        self.selected_option = 0

        self.door_unlocked = False
        self.highscore_list = []
        self.load_highscores()
        self.name = ""


        self.width, self.height = 960, 640
        self.draw = Draw(self)
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("Robot Escape")
        self.state = "menu"
        self.running = True

        self.game_time = 0
        self.start_time = None

        self.arena = Arena(self)

        self.coin_list = []
        self.coin_positions = [
                                (2, 1),
                                (11, 1),
                                (20, 1),
                                (2, 6),
                                (12, 6),
                                (23, 5),
                                (3, 12),
                                (20, 10)
                            ]

    def run(self):
        while self.running:
            self.dt = self.clock.tick(60) / 1000
            self.handle_events()
            self.update()
            self.draw.draw()
        pygame.quit()

    def update(self):
        if self.state == "playing":
            self.game_time = time.monotonic() - self.start_time
            new_position = self.player.move()
            self.arena.wall_slide(self.player, new_position)

            for fire_area in self.arena.fire_areas:
                fire_area.update(self.game_time)

            if self.arena.player_on_fire():
                self.player.health -= self.arena.fire_dmg * self.dt
            if self.player.health <= 0:
                self.player.health = 0
                self.state = "game_over"
                return

            self.update_monster()
            for monster in self.monster_list:
                if monster.collision.colliderect(self.player.collision):
                    self.player.health = 0
                    self.state = "game_over"
                    return

            self.collected_coins()
            self.unlock_door()
            self.game_won()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "enter_name":
                self.handle_name_input(event)
                continue

            if event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    self.handle_menu_input(event)
                elif self.state == "highscores":
                    self.handle_highscores_input(event)
                elif self.state == "playing":
                    self.handle_playing_input(event)
                elif self.state == "game_over":
                    self.handle_game_over_input(event)
                elif self.state == "victory":
                    self.handle_game_won_input(event)

    def handle_menu_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options)
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.state = self.menu_states[self.selected_option]
            if self.state == "playing":
                self.restart_game()

    def handle_highscores_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "menu"

    def handle_playing_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.state = "menu"

    def handle_game_over_input(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.restart_game()
        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"

    def handle_game_won_input(self, event):
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.restart_game()
        elif event.key == pygame.K_ESCAPE:
            self.state = "menu"

    def handle_name_input(self, event):
        if event.type == pygame.TEXTINPUT:
            if len(self.name) + len(event.text) <= 15:
                self.name += event.text

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.name = self.name[:-1]

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self.name.strip():
                    self.name = self.name.strip()
                    self.save_score()
                    pygame.key.stop_text_input()
                    self.state = "victory"

    def save_score(self):
        highscore = {"name": self.name, "time": self.final_time}
        self.highscore_list.append(highscore)
        sorted_list = sorted(self.highscore_list, key=lambda score: score["time"])
        self.highscore_list = sorted_list[:5]
        self.write_highscores()

    def update_monster(self):
        for monster in self.monster_list:
            self.update_monster_state(monster)
            self.move_monster(monster)

    def update_monster_state(self, monster):
        if monster.player_in_range(self.player) and self.arena.has_los(monster):
            monster.state = "chasing"
            monster.last_seen_player = self.player.collision.center
            monster.idle_since = None

        elif monster.last_seen_player is not None:
            monster.state = "searching"

        elif monster.state != "returning":
            monster.state = "idle"

    def move_monster(self, monster):
        if monster.state == "idle":
            monster.path = []
            monster.path_goal = None

            if monster.collision.center == monster.monster_spawn:
                monster.idle_since = None
                return

            if monster.idle_since is None:
                monster.idle_since = self.game_time

            if self.game_time - monster.idle_since < 3:
                return

            monster.state = "returning"
            monster.idle_since = None

        if monster.state == "chasing":
            destination = self.player.collision.center

        elif monster.state == "searching":
            if monster.last_seen_player is None:
                monster.state = "idle"
                monster.path = []
                monster.path_goal = None
                return
            destination = monster.last_seen_player

        elif monster.state == "returning":
            destination = monster.monster_spawn

        else:
            return

        monster_tile = self.arena.position_to_tile(*monster.collision.center)
        goal_tile = self.arena.position_to_tile(*destination)

        can_repath = (not monster.path or monster.collision.center == self.arena.tile_rect(*monster.path[0]).center)

        if can_repath and (monster.path_goal != goal_tile or (not monster.path and monster_tile != goal_tile)):
            monster.path = self.arena.find_path(monster_tile, goal_tile)
            monster.path_goal = goal_tile

            if monster.path:
                monster.path.insert(0, monster_tile)
            elif monster_tile != goal_tile:
                if monster.state == "searching":
                    monster.state = "idle"
                    monster.last_seen_player = None
                    monster.path_goal = None
                    monster.idle_since = self.game_time
                return

        while monster.path:
            target = self.arena.tile_rect(*monster.path[0]).center
            if monster.collision.center != target:
                break
            monster.path.pop(0)

        if not monster.path:
            target = destination
            target_position = monster.collision.copy()
            target_position.center = target
            if not self.arena.valid_position(target_position, monster):
                target = self.arena.tile_rect(*goal_tile).center

        old_center = monster.collision.center
        new_position = monster.move_towards(target)
        self.arena.wall_slide(monster, new_position)

        if monster.collision.center == old_center and old_center != target:
            monster.path = []
            monster.path_goal = None
            return

        if (monster.state in ("searching", "returning") and not monster.path and monster.collision.center == target):
            monster.state = "idle"
            monster.last_seen_player = None
            monster.path_goal = None
            monster.idle_since = self.game_time

    def unlock_door(self):
        if not self.coin_list and not self.door_unlocked:
            self.arena.place_tiles(11, 21, 3, 1, "N")
            self.arena.place_tiles(12, 21, 1, 2, "N")
            self.door_unlocked = True

    def collected_coins(self):
        for t in self.coin_list[:]:
            if t.collision.colliderect(self.player.collision):
                self.coin_list.remove(t)

    def game_won(self):
        if self.door_unlocked and self.player.collision.colliderect(self.door_rect):
            self.final_time = self.game_time
            if (len(self.highscore_list) < 5 or self.final_time < self.highscore_list[-1]["time"]):
                self.name = ""
                self.state = "enter_name"
                pygame.key.start_text_input()
            else:
                self.state = "victory"

    def restart_game(self):
        self.player.health = 100
        self.player.collision.topleft = self.player_spawn
        self.game_time = 0
        self.start_time = time.monotonic()
        self.state = "playing"
        self.reset_coins()
        self.reset_monster()
        self.arena.place_tiles(11, 21, 3, 1, "W")
        self.arena.place_tiles(12, 21, 1, 2, "W")
        self.door_unlocked = False

    def reset_coins(self):
        self.coin_list.clear()
        for column, row in self.coin_positions:
            rect = self.arena.tile_rect(row, column)
            coin = Coin(rect.x, rect.y, self.coin)
            self.coin_list.append(coin)

    def reset_monster(self):
        self.monster_list.clear()
        for column, row in self.monster_positions:
            rect = self.arena.tile_rect(row, column)
            monster = Monster(rect.x, rect.y, self.monster)
            monster.collision.center = rect.center
            monster.monster_spawn = monster.collision.center
            self.monster_list.append(monster)

    def write_highscores(self):
        with open("highscores.json", "w", encoding="utf-8") as file:
            json.dump(self.highscore_list, file, indent=4)

    def load_highscores(self):
        try:
            with open("highscores.json", "r", encoding="utf-8") as file:
                self.highscore_list = json.load(file)
        except FileNotFoundError:
            self.highscore_list = []