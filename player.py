import arcade

from genome import Genome


class Player:

    size_x = 100
    size_y = 50
    genome_inputs = 4
    genome_outputs = 2 # Up or down?

    def __init__(self, game):
        self.game = game
        self.top = game.top
        self.middle = game.middle
        self.bottom = game.bottom
        self.position_x = 0.075 * game.width
        self.position_y = game.middle
        self.speed_x = 0
        self.speed_y = 0
        self.color = (255, 255, 255)
        self.speed = 10
        self.dead = False
        self.next_lane = None
        self.fitness = 0
        self.unadjusted_fitness = 0
        self.lifespan = 0
        self.best_score = 0
        self.replay = False
        self.score = 0
        self.gen = 0
        self.vision = [0 for _ in range(self.genome_inputs)]
        self.decision = [0 for _ in range(self.genome_outputs)]
        self.brain = Genome(self.genome_inputs, self.genome_outputs)

    def draw(self):
        arcade.draw_rectangle_filled(self.position_x, self.position_y,
                                     self.size_x, self.size_y, self.color)

    def update(self):
        self.increment_counters()

        if self.next_lane == None:
            if self.speed_y > 0:
                if self.position_y == self.bottom:
                    self.next_lane = self.middle
                elif self.position_y == self.middle:
                    self.next_lane = self.top
            elif self.speed_y < 0:
                if self.position_y == self.top:
                    self.next_lane = self.middle
                elif self.position_y == self.middle:
                    self.next_lane = self.bottom
        else:
            if self.speed_y > 0:
                if (self.next_lane == self.middle
                    and self.position_y >= self.middle):
                    self.next_lane = None
                    self.position_y = self.middle
                    self.speed_y = 0
                elif (self.next_lane == self.top
                      and self.position_y >= self.top):
                    self.next_lane = None
                    self.position_y = self.top
                    self.speed_y = 0
                else:
                    self.position_y += self.speed_y
            if self.speed_y < 0:
                if (self.next_lane == self.middle
                    and self.position_y <= self.middle):
                    self.next_lane = None
                    self.position_y = self.middle
                    self.speed_y = 0
                elif (self.next_lane == self.bottom
                      and self.position_y <= self.bottom):
                    self.next_lane = None
                    self.position_y = self.bottom
                    self.speed_y = 0
                else:
                    self.position_y += self.speed_y

        for enemy in self.game.enemy_list:
            if enemy.collided(self):
                self.dead = True
                break

    def move(self, direction):
        if self.next_lane == None:
            if direction == 'up':
                self.speed_y = self.speed
            elif direction == 'down':
                self.speed_y = -self.speed

    def clone(self):
        clone = Player(self.game)
        clone.brain = self.brain.clone()
        clone.fitness = self.fitness
        clone.unadjusted_fitness = self.unadjusted_fitness
        clone.brain.generate_network()
        clone.gen = self.gen
        clone.best_score = self.best_score
        clone.color = self.color

        return clone

    def calculate_fitness(self):
        self.unadjusted_fitness = self.score*self.score
        self.fitness = self.unadjusted_fitness

    def crossover(self, parent_2):
        child = Player(self.game)
        child.color = self.color
        child.brain = self.brain.crossover(parent_2.brain)
        child.brain.generate_network()
        
        return child

    def look(self):
        if len(self.game.enemy_list) > 0:
            dist_min_bot = 1e6
            dist_min_mid = 1e6
            dist_min_top = 1e6

            for enemy in self.game.enemy_list:
                dist = enemy.position_x - self.position_x
                if dist <= 0:
                    continue
                if enemy.position_y == self.bottom:
                    if dist < dist_min_bot:
                        dist_min_bot = dist
                if enemy.position_y == self.middle:
                    if dist < dist_min_mid:
                        dist_min_mid = dist
                if enemy.position_y == self.top:
                    if dist < dist_min_top:
                        dist_min_top = dist

            self.vision[0] = (dist_min_bot/self.game.width
                              if dist_min_bot != 1e6
                              else 1)
            self.vision[1] = (dist_min_mid/self.game.width
                              if dist_min_mid != 1e6
                              else 1)
            self.vision[2] = (dist_min_top/self.game.width
                              if dist_min_top != 1e6
                              else 1)

        else:
            self.vision[0] = 1
            self.vision[1] = 1
            self.vision[2] = 1
        self.vision[3] = self.position_y/self.game.height

    def think(self):
        decision = self.brain.feed_forward(self.vision)

        action_certainty = max(decision)
        action_taken = decision.index(action_certainty)

        if action_taken == 0:
            self.move('up')
        elif action_taken == 1:
            self.move('down')

    def increment_counters(self):
        self.lifespan += 1

        if self.lifespan % 5 == 0:
            self.score += 1
