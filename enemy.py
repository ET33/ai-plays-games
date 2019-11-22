import arcade


class Enemy:

    speed_x = -7.5
    size_x = 50
    size_y = 50
    color = (255, 55, 55)

    def __init__(self, position_x, position_y):
        self.position_x = position_x
        self.position_y = position_y
        self.dead = False

    def draw(self):
        """Draw itself on the screen."""
        arcade.draw_rectangle_filled(self.position_x, self.position_y,
                                     self.size_x, self.size_y, self.color)

    def update(self):
        """Update state of itself."""
        self.position_x += self.speed_x
        if self.position_x + self.size_x / 2 < 0: # Out of bounds
            self.dead = True

    def collided(self, player):
        """Check collision with given player."""
        if (player.position_x - player.size_x / 2
            < self.position_x + self.size_x / 2
            and player.position_x + player.size_x / 2
            > self.position_x - self.size_x / 2
            and player.position_y - player.size_y / 2
            < self.position_y + self.size_y / 2
            and player.position_y + player.size_y / 2
            > self.position_y - self.size_y / 2):
            return True
        else:
            return False
