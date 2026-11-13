import pygame

class Draw:
    def __init__(self, game):
        self.game = game
        self.window = pygame.display.set_mode((self.game.width, self.game.height))
        self.title_font = pygame.font.SysFont("Arial", 56)
        self.menu_font = pygame.font.SysFont("Arial", 32)
        self.small_font = pygame.font.SysFont("Arial", 20)

    def draw(self):
        self.window.fill((0, 0, 0))

        if self.game.state == "menu":
            self.draw_menu()
        elif self.game.state == "highscores":
            self.draw_highscores()
        elif self.game.state == "playing":
            self.draw_game()
        elif self.game.state == "game_over":
            self.draw_game_over()
        elif self.game.state == "victory":
            self.draw_game_won()
        elif self.game.state == "enter_name":
            self.draw_name_entry()

        pygame.display.flip()

    def draw_menu(self):
        self.draw_text("Robot Escape", self.title_font, (255, 255, 255), self.game.width // 2, 160)
        for index, option in enumerate(self.game.menu_options):
            y = 300 + index * 60
            if index == self.game.selected_option:
                colour = 255, 255, 0

                text_width, text_height = self.get_text_size(option, self.menu_font)

                padding_x = 20
                padding_y = 10

                box_width = text_width + padding_x * 2
                box_height = text_height + padding_y * 2

                pygame.draw.rect(
                    self.window,
                    (colour),
                    (
                        self.game.width // 2 - box_width / 2,
                        y - box_height / 2,
                        box_width,
                        box_height
                    ),
                    3
                )
            else:
                colour = 255, 255, 255        
            self.draw_text(option, self.menu_font, colour, 480, y)

    def draw_highscores(self):
        self.draw_text("Highscores", self.title_font,
            (255, 255, 255), self.game.width // 2, 80)

        for i, highscore in enumerate(self.game.highscore_list):
            y = 170 + i * 50

            self.draw_text(f"{i + 1}.", self.menu_font,
                (255, 255, 255), 270, y)

            self.draw_text(highscore["name"], self.menu_font,
                (255, 255, 255), 420, y)

            self.draw_text(f'{highscore["time"]:.2f} s', self.menu_font,
                (255, 255, 255), 650, y)

        self.draw_text("Press ESC to return", self.small_font,
            (180, 180, 180), self.game.width // 2, 570)

    def draw_game(self):
        self.draw_arena()
        self.draw_fire_area()
        self.draw_coin()
        self.window.blit(self.game.door, self.game.door_rect)
        self.draw_monster()
        self.window.blit(self.game.player.robot, self.game.player.collision)

        self.draw_text(f"Health: {self.game.player.health:.0f}",
        self.menu_font,
        (255, 0, 0),
        870, 37)

        self.draw_text(f"Time: {self.game.game_time:.1f}",
        self.menu_font,
        (255, 255, 255),
        680, 37 )

        self.draw_text(f"Coins: {len(self.game.coin_positions) - len(self.game.coin_list)}",
        self.menu_font,
        (255, 255, 0),
        70, 37)


    def draw_text(self, text, font, colour, x, y):
        final_text = font.render(text, True, colour)
        text_width, text_height = self.get_text_size(text, font)
        self.window.blit(final_text, (x - text_width / 2, y - text_height / 2))

    def draw_arena(self):
        for index_y, row in enumerate(self.game.arena.arena):
            for index_x, tile in enumerate(row):
                x = index_x * self.game.arena.tile_size
                y = index_y * self.game.arena.tile_size + self.game.arena.hud_height
                pygame.draw.rect(
                    self.window,
                    (self.game.arena.tile_colours[tile]),
                    (x, y, self.game.arena.tile_size, self.game.arena.tile_size)
                )
                pygame.draw.rect(
                    self.window,
                    (self.game.arena.tile_outlines[tile]),
                    (x, y, self.game.arena.tile_size, self.game.arena.tile_size),
                    1
                )

    def draw_fire_area(self):
        for fire_area in self.game.arena.fire_areas:
            if fire_area.phase == "inactive":
                continue
            if fire_area.phase == "warning":
                colour = 255, 145, 0
            elif fire_area.phase == "burning":
                colour = 255, 0, 0
            pygame.draw.rect(
                self.window,
                colour,
                (self.game.arena.tile_rect(*fire_area.area))
            )

    def draw_name_entry(self):
        self.draw_text("NEW HIGHSCORE!", self.title_font,
            (255, 215, 0), self.game.width // 2, 170)

        self.draw_text(f"Completion time: {self.game.final_time:.2f} s",
            self.menu_font, (255, 255, 255),
            self.game.width // 2, 260)

        self.draw_text("Enter your name:", self.menu_font,
            (255, 255, 255), self.game.width // 2, 340)

        self.draw_text(self.game.name + "_", self.menu_font,
            (255, 255, 0), self.game.width // 2, 400)

        self.draw_text("Press ENTER to save", self.small_font,
            (180, 180, 180), self.game.width // 2, 490)

    def draw_coin(self):
        for t in self.game.coin_list:
            self.window.blit(t.coin, t.collision)

    def draw_monster(self):
        for t in self.game.monster_list:
            self.window.blit(t.monster, t.collision)

    def draw_game_over(self):
        self.draw_text("GAME OVER", self.title_font, (255, 0, 0), self.game.width / 2, 250)
        self.draw_end_game()

    def draw_game_won(self):
        self.draw_text("VICTORY", self.title_font, (0, 255, 0), self.game.width / 2, 250)
        self.draw_end_game()
        self.draw_text(f"Your time was {self.game.final_time:.1f} seconds", self.menu_font, (0, 255, 0), self.game.width / 2, 400)

    def draw_end_game(self):
        self.draw_text("Press ENTER to retry", self.menu_font, (255, 255, 255), self.game.width / 2, 310 )
        self.draw_text("Press ESC to go back to menu", self.menu_font, (255, 255, 255), self.game.width / 2, 355)

    def get_text_size(self, text, font):
        return font.size(text)