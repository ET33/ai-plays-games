"""remove all elements in list python
This simple animation example shows how to move an item with the keyboard.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.move_keyboard
"""

import arcade
import random

from player import Player
from enemy import Enemy
from population import Population

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Game"
MOVEMENT_SPEED = 10
TOP = SCREEN_HEIGHT/2 + SCREEN_HEIGHT/3
MIDDLE = SCREEN_HEIGHT/2
BOTTOM = SCREEN_HEIGHT/2 - SCREEN_HEIGHT/3
CAR_WIDTH = 100
CAR_HEIGHT = 50

class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.BLACK_OLIVE)

        self.update_rate = 1/60
        self.set_update_rate(self.update_rate)
        self.enemy_list = []
        self.frame_counter = 0
        self.display_info = True
        self.pop = Population(500, self.enemy_list)
        self.show_nothing = False

    def on_draw(self):
        """ Called whenever we need to draw the window. """
        if self.show_nothing == True:
            return

        arcade.start_render()

        max_fitness = 0
        player_to_draw = 0

        for player in self.pop.pop:
            if player.fitness >= max_fitness and not player.dead:
                player_to_draw = player
                max_fitness = player.fitness

        arcade.draw_text("Current player \n\n" + \
                         "Score: " + str(player_to_draw.score) + "\n" + \
                         "Fitness: " + str(int(player_to_draw.fitness)), \
                         0.01*SCREEN_WIDTH, 0.9*SCREEN_HEIGHT,
                         arcade.color.WHITE, 12)

        player_to_draw.draw()
            
        for enemy in self.enemy_list:
            enemy.draw()

    def on_update(self, delta_time):
        if self.pop.done() != True:
            self.frame_counter += 1
            if (self.frame_counter % 30 == 0):
                location = [BOTTOM, MIDDLE, TOP]
                index = random.randrange(len(location))
                enemy = Enemy(SCREEN_WIDTH, location[index], -10, 0, CAR_HEIGHT, arcade.color.ANDROID_GREEN)
                self.enemy_list.append(enemy)

            for i, enemy in enumerate(self.enemy_list):
                enemy.update()
                if enemy.dead:
                    del self.enemy_list[i]

            self.pop.update_alive()
            if self.display_info == True:
                print(f"Gen {self.pop.gen}")
                print(f"Best score: {self.pop.best_score}")
            self.display_info = False
        else:
            self.pop.natural_selection()
            self.reset_enemies()
            self.display_info = True

    def on_key_press(self, key, modifiers):
        """ Called whenever the user presses a key. """
        if key == arcade.key.LEFT:
            self.update_rate += 1/30
            self.set_update_rate(self.update_rate)
        elif key == arcade.key.RIGHT:
            self.update_rate -= 1/30
            self.set_update_rate(self.update_rate)
        elif key == arcade.key.H:
            self.show_nothing = not self.show_nothing
            if self.show_nothing == True:
                self.set_update_rate(1e-6)
            else:
                self.set_update_rate(self.update_rate)



    def on_key_release(self, key, modifiers):
        """ Called whenever a user releases a key. """

    def reset_enemies(self):
        del self.enemy_list[:]

def main():
    Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()
