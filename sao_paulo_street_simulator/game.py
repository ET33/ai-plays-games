"""A Neuroevolution of Augmenting Topologies (NEAT) method implementation for
training neural networks to play games.
"""

import arcade
import random

from player import Player
from enemy import Enemy
from population import Population


class Game(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.gap_factor = 0.25
        self.top = self.height/2 + self.gap_factor * self.height
        self.middle = self.height/2
        self.bottom = self.height/2 - self.gap_factor * self.height
        self.show_game = True
        self.enemy_list = []
        self.frame_counter = 0
        self.display_info = True
        self.pop = Population(250, self)
        arcade.set_background_color(arcade.color.BLACK_OLIVE)

    def on_draw(self):
        """Called whenever we need to draw the window."""
        arcade.start_render()
        if not self.show_game:
            return

        players = [player for player in self.pop.pop.copy() if not player.dead]
        players.sort(key=lambda x: x.fitness, reverse=True)
        players_to_draw = min(len(players), 5)

        for i in range(players_to_draw):
            players[i].draw()

        if not self.pop.done():
            arcade.draw_text(f"Generation {self.pop.gen}\n\n"
                             + f"Overall best score: {self.pop.best_score}",
                             0.01 * self.width, 0.01 * self.height,
                             arcade.color.WHITE, 14)
            arcade.draw_text("Current top player\n\n"
                             + f"Score: {players[0].score}\n"
                             + f"Fitness: {players[0].fitness}",
                             0.99 * self.width, 0.01 * self.height,
                             arcade.color.WHITE, 14,
                             align='right', anchor_x='right')
            
        for enemy in self.enemy_list:
            enemy.draw()

    def on_update(self, delta_time):
        if self.pop.done() != True:
            self.frame_counter += 1
            if (self.frame_counter % 30 == 0):
                location = [self.bottom, self.middle, self.top]
                index = random.randrange(len(location))
                enemy = Enemy(self.width, location[index])
                self.enemy_list.append(enemy)

            for i, enemy in enumerate(self.enemy_list):
                enemy.update()
                if enemy.dead:
                    del self.enemy_list[i]
            self.enemy_list[:] = [enemy for enemy in self.enemy_list
                                  if not enemy.dead]

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
        if key == arcade.key.H:
           self.show_game = not self.show_game

    def on_key_release(self, key, modifiers):
        """Called whenever a user releases a key."""

    def reset_enemies(self):
        del self.enemy_list[:]


def main():

    screen_title = "NEAT!"
    aspect_ratio = (16, 9)
    scale_factor = 78
    resolution = ([scale_factor * dimension for dimension in aspect_ratio])

    game = Game(resolution[0], resolution[1], screen_title)
    arcade.run()


if __name__ == "__main__":
    main()
