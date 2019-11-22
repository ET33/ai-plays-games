import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Game"
MOVEMENT_SPEED = 10
TOP = SCREEN_HEIGHT/2 + SCREEN_HEIGHT/3
MIDDLE = SCREEN_HEIGHT/2
BOTTOM = SCREEN_HEIGHT/2 - SCREEN_HEIGHT/3
CAR_WIDTH = 100
CAR_HEIGHT = 50

class Enemy:
    def __init__(self, position_x, position_y, change_x, change_y, radius,
                 color):
        self.position_x = position_x
        self.position_y = position_y
        self.change_x = change_x
        self.change_y = change_y
        self.radius = radius
        self.color = color
        self.dead = False

    def draw(self):
        arcade.draw_rectangle_filled(self.position_x, self.position_y,
                                     self.radius, self.radius, self.color)

    def update(self):
        self.position_x += self.change_x
        if self.position_x + self.radius/2 < 0:
            self.dead = True

    def collided(self, player):
        if (player.position_x - CAR_WIDTH / 2
            < self.position_x + self.radius / 2
            and player.position_x + CAR_WIDTH / 2
            > self.position_x - self.radius / 2
            and player.position_y - CAR_HEIGHT / 2
            < self.position_y + self.radius / 2
            and player.position_y + CAR_HEIGHT / 2
            > self.position_y - self.radius / 2):
            return True
        else:
            return False
