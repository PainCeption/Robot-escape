from pathlib import Path
import pygame

class Player:
    def __init__(self, x, y):
        self.robot = pygame.image.load(str(Path(__file__).parent / "assets" / "robot.png"))
        self.width = self.robot.get_width()
        self.height = self.robot.get_height()
        self.collision = pygame.Rect(x, y, self.width, self.height)
        self.speed = 4
        self.health = 100

    def get_feet_rect(self):
        feet = pygame.Rect(0, 0, 28, 10)
        feet.midbottom = self.collision.midbottom
        return feet

    def get_body_rect(self, position):
        body = pygame.Rect(0, 0, 38, 56)
        body.midbottom = position.midbottom
        return body

    def move(self):
        new_position = self.collision.copy()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            new_position.x += self.speed
        elif keys[pygame.K_LEFT]:
            new_position.x -= self.speed
        if keys[pygame.K_UP]:
            new_position.y -= self.speed
        elif keys[pygame.K_DOWN]:
            new_position.y += self.speed
        return new_position

class Monster:
    def __init__(self, x, y, image):
        self.monster = image
        self.width = self.monster.get_width()
        self.height = self.monster.get_height()
        self.collision = pygame.Rect(x, y, self.width, self.height)
        self.monster_spawn = (x, y)
        self.last_seen_player = None
        self.speed = 2
        self.state = "idle"
        self.detection_range = 200
        self.path = []
        self.path_goal = None
        self.idle_since = None
    
    def get_body_rect(self, position):
        body = pygame.Rect(0, 0, 28, 28)
        body.center = position.center
        return body

    def player_in_range(self, player):
        monster_pos = pygame.Vector2(self.collision.center)
        player_pos = pygame.Vector2(player.collision.center)
        distance = monster_pos.distance_to(player_pos)
        return distance <= self.detection_range


    def move_towards(self, target):
        current = pygame.Vector2(self.collision.center)
        destination = pygame.Vector2(target)
        direction = destination - current
        if direction.length_squared() == 0:
            return self.collision.copy()

        movement = direction.normalize() * min(self.speed, direction.length())
        new_position = self.collision.copy()
        new_position.center = current + movement
        return new_position

class Coin:
    def __init__(self, x, y, image):
        self.coin = image
        self.collision = pygame.Rect(x, y, 40, 40) 