import pygame
from collections import deque
from characters import Monster
from fire_area import FireArea

class Arena:
    def __init__(self, game):
        self.game = game

        self.tile_size = 40
        self.hud_height = 80
        self.arena = [["N" for x in range(24)] for y in range(14)]
        self.tile_colours = {
                            "N": (53, 59, 54),
                            "W": (100, 116, 139),
                            "F": (53, 59, 54),
                            "S": (53, 59, 54)
                        }
        self.tile_outlines = {
                            "N": (81, 90, 83),
                            "W": (203, 213, 225),
                            "F": (239, 68, 68),
                            "S": (74, 222, 128)
                        }

        #Generating appropiate tiles
        self.place_tiles(3, 0, 3, 2, "W")
        self.place_tiles(3, 6, 4, 2, "W")
        self.place_tiles(3, 13, 4, 2, "W")
        self.place_tiles(3, 20, 4, 2, "W")
        self.place_tiles(8, 2, 4, 2, "W")
        self.place_tiles(8, 9, 4, 2, "W")
        self.place_tiles(8, 16, 1, 2, "W")
        self.place_tiles(8, 19, 1, 2, "W")
        self.place_tiles(0, 7, 2, 2, "W")
        self.place_tiles(5, 4, 2, 2, "W")
        self.place_tiles(5, 19, 2, 2, "W")
        self.place_tiles(11, 7, 2, 2, "W")
        self.place_tiles(11, 14, 2, 2, "W")

        #location of the door
        self.place_tiles(11, 21, 3, 1, "W")
        self.place_tiles(12, 21, 1, 2, "W")

        #firetiles
        self.place_tiles(5, 1, 3, 3, "F")
        self.place_tiles(3, 10, 3, 5, "F")
        self.place_tiles(10, 5, 2, 4, "F")
        self.place_tiles(9, 20, 2, 1, "F")
        self.place_tiles(10, 19, 3, 1, "F")
        self.place_tiles(11, 19, 2, 1, "F")
        self.fire_areas = [
                            FireArea((5, 1, 3, 3)),
                            FireArea((3, 10, 3, 5)),
                            FireArea((10, 5, 2, 4)),
                            FireArea((9, 20, 2, 1)),
                            FireArea((10, 19, 3, 1)),
                            FireArea((11, 19, 2, 1))
                        ]
        self.fire_dmg = 25 #HP per second

    def wall_slide(self, character, new_position):
        x_position = character.collision.copy()
        x_position.x = new_position.x

        if self.valid_position(x_position, character):
            character.collision.x = x_position.x

        y_position = character.collision.copy()
        y_position.y = new_position.y
        if self.valid_position(y_position, character):
            character.collision.y = y_position.y

    def player_on_fire(self):
        hit_box = self.game.player.get_feet_rect()
        for fire_area in self.fire_areas:
            if fire_area.phase == "burning":
                fire_hit_box = self.tile_rect(*fire_area.area)
                if hit_box.colliderect(fire_hit_box):
                    return True
        return False

    def find_path(self, start, goal):
        queue = deque([start])
        visited = {start}
        came_from = {}

        while queue:
            current = queue.popleft()
            if current == goal:
                break
            neighbour_tiles = self.get_neightbours(*current)
            for tiles in neighbour_tiles:
                if tiles not in visited:
                    came_from[tiles] = current
                    queue.append(tiles)
                    visited.add(tiles)
        if goal not in visited:
            return []
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
            
    def place_tiles(self, row, column, width, height, tile_type):
        for y in range(row, row + height):
            for x in range(column, column + width):
                self.arena[y][x] = tile_type

    def valid_position(self, new_position, character):
        body = character.get_body_rect(new_position)
        bounds = body if isinstance(character, Monster) else new_position
        if bounds.left < 0:
            return False
        elif bounds.top < self.hud_height:
            return False
        elif bounds.bottom > self.game.height:
            return False
        elif bounds.right > self.game.width:
            return False

        for index_y, row in enumerate(self.arena):
            for index_x, tile in enumerate(row):
                if tile == "W":
                    x = index_x * self.tile_size
                    y = index_y * self.tile_size + self.hud_height
                    wall_rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                    if body.colliderect(wall_rect):
                        return False
        return True

    def has_los(self, monster):
        start = monster.collision.center
        end = self.game.player.collision.center
        for index_y, row in enumerate(self.arena):
            for index_x, tile in enumerate(row):
                if tile == "W":
                    wall_rect = self.tile_rect(index_y, index_x)
                    if wall_rect.clipline(start, end):
                        return False
        return True

    def tile_rect(self, row, column, width=1, height=1):
        x = column * self.tile_size
        y = row * self.tile_size + self.hud_height
        width = width * self.tile_size
        height = height * self.tile_size
        return pygame.Rect(x, y, width, height)

    def position_to_tile(self, x, y):
        row = (y - self.hud_height) // self.tile_size
        column = x // self.tile_size
        return row, column

    def get_neightbours(self, row, column):
        valid_neighbours = []
        direction_list =(
                        (row - 1, column),
                        (row + 1, column),
                        (row, column - 1),
                        (row, column + 1)
        )
        for row, column in direction_list:
            if not 0 <= row < len(self.arena):
                continue
            if not 0 <= column < len(self.arena[0]):
                continue
            if self.arena[row][column] == "W":
                continue
            valid_neighbours.append((row, column))
        return valid_neighbours