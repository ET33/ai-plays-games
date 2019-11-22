"""A Neuroevolution of Augmenting Topologies (NEAT) method implementation for
training neural networks to play games.
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

SHOW_GAME = True

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

    def on_draw(self):
        """Called whenever we need to draw the window."""
        arcade.start_render()

        players = [player for player in self.pop.pop.copy() if not player.dead]
        players.sort(key=lambda x: x.fitness, reverse=True)
        players_to_draw = min(len(players), 5)

        for i in range(players_to_draw):
            players[i].draw()

        if not self.pop.done():
            arcade.draw_text("Current player \n\n"
                             + "Score: " + str(players[0].score) + "\n"
                             + "Best fitness: " + str(int(players[0].fitness)),
                             0.01 * SCREEN_WIDTH, 0.9 * SCREEN_HEIGHT,
                             arcade.color.WHITE, 12)
            
        for enemy in self.enemy_list:
            enemy.draw()

    def on_update(self, delta_time):
        if self.pop.done() != True:
            self.frame_counter += 1
            if (self.frame_counter % 30 == 0):
                location = [BOTTOM, MIDDLE, TOP]
                index = random.randrange(len(location))
                enemy = Enemy(SCREEN_WIDTH, location[index], -7.5, 0,
                              CAR_HEIGHT, arcade.color.ANDROID_GREEN)
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
        """Called whenever the user presses a key."""

    def on_key_release(self, key, modifiers):
        """Called whenever a user releases a key."""

    def reset_enemies(self):
        del self.enemy_list[:]

def main():
    if SHOW_GAME == True:
        Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.run()
    else:
        enemy_list = []
        pop = Population(500, enemy_list)
        frame_counter = 0

        while True:
            if pop.done() != True:
                frame_counter += 1
                if (frame_counter % 30 == 0):
                    location = [BOTTOM, MIDDLE, TOP]
                    index = random.randrange(len(location))
                    enemy = Enemy(SCREEN_WIDTH, location[index], -7.5, 0,
                                  CAR_HEIGHT, arcade.color.ANDROID_GREEN)
                    enemy_list.append(enemy)

                for i, enemy in enumerate(enemy_list):
                    enemy.update()
                    if enemy.dead:
                        del enemy_list[i]

                pop.update_alive()
            else:
                print(f"Gen {pop.gen}")
                print(f"Best score: {pop.best_score}")
                pop.natural_selection()
                del enemy_list[:]


if __name__ == "__main__":
    main()
