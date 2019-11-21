import arcade

from genome import Genome

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Game"
TOP = SCREEN_HEIGHT/2 + SCREEN_HEIGHT/3
MIDDLE = SCREEN_HEIGHT/2
BOTTOM = SCREEN_HEIGHT/2 - SCREEN_HEIGHT/3
CAR_WIDTH = 100
CAR_HEIGHT = 50

class Player:
    def __init__(self, enemy_list):
        # Take the parameters of the init function above, and create instance variables out of them.
        self.position_x = 0.1*SCREEN_WIDTH
        self.position_y = MIDDLE
        self.change_x = 0
        self.change_y = 0
        self.size_x = CAR_WIDTH
        self.size_y = CAR_HEIGHT
        self.color = (255, 255, 255)
        self.speed = 10
        self.dead = False
        self.next_lane = None
        self.enemy_list = enemy_list

        self.fitness = 0
        self.unadjusted_fitness = 0
        self.lifespan = 0
        self.best_score = 0
        self.replay = False
        self.score = 0
        self.gen = 0

        self.genome_inputs = 4 
        self.genome_outputs = 2 # up or down?

        self.vision = [0 for _ in range(self.genome_inputs)]
        self.decision = [0 for _ in range(self.genome_outputs)]

        self.brain = Genome(self.genome_inputs, self.genome_outputs)

    def draw(self):
        arcade.draw_rectangle_filled(self.position_x, self.position_y, self.size_x, self.size_y, self.color)

    def update(self):
        self.increment_counters()

        if self.next_lane == None:
            if self.change_y > 0:
                if self.position_y == BOTTOM:
                    self.next_lane = MIDDLE
                elif self.position_y == MIDDLE:
                    self.next_lane = TOP
            elif self.change_y < 0:
                if self.position_y == TOP:
                    self.next_lane = MIDDLE
                elif self.position_y == MIDDLE:
                    self.next_lane = BOTTOM
        else:
            if self.change_y > 0:
                if self.next_lane == MIDDLE and self.position_y >= MIDDLE:
                    self.next_lane = None
                    self.position_y = MIDDLE
                    self.change_y = 0
                elif self.next_lane == TOP and self.position_y >= TOP:
                    self.next_lane = None
                    self.position_y = TOP
                    self.change_y = 0
                else:
                    self.position_y += self.change_y
            if self.change_y < 0:
                if self.next_lane == MIDDLE and self.position_y <= MIDDLE:
                    self.next_lane = None
                    self.position_y = MIDDLE
                    self.change_y = 0
                elif self.next_lane == BOTTOM and self.position_y <= BOTTOM:
                    self.next_lane = None
                    self.position_y = BOTTOM
                    self.change_y = 0
                else:
                    self.position_y += self.change_y

        for enemy in self.enemy_list:
            if enemy.collided(self):
                self.dead = True
                break

    def move(self, direction):
        if self.next_lane == None:
            if direction == 'up':
                self.change_y = self.speed
            elif direction == 'down':
                self.change_y = -self.speed

    def clone(self):
        clone = Player(self.enemy_list)
        clone.brain = self.brain.clone()
        clone.fitness = self.fitness
        clone.brain.generate_network()
        clone.gen = self.gen
        clone.best_score = self.best_score
        clone.color = self.color

        return clone

    def calculate_fitness(self):
        self.fitness = self.score*self.score

    def crossover(self, parent_2):
        child = Player(self.enemy_list)
        child.brain = self.brain.crossover(parent_2.brain)
        child.brain.generate_network()
        
        return child

    def look(self):
        if len(self.enemy_list) > 0:
            dist_min_bot = 1e6
            dist_min_mid = 1e6
            dist_min_top = 1e6

            for enemy in self.enemy_list:
                dist = enemy.position_x - self.position_x
                if enemy.position_y == BOTTOM:
                    if dist < dist_min_bot:
                        dist_min_bot = dist
                if enemy.position_y == MIDDLE:
                    if dist < dist_min_mid:
                        dist_min_mid = dist
                if enemy.position_y == TOP:
                    if dist < dist_min_top:
                        dist_min_top = dist

            self.vision[0] = dist_min_bot/SCREEN_WIDTH if dist_min_bot != 1e6 else 1
            self.vision[1] = dist_min_mid/SCREEN_WIDTH if dist_min_mid != 1e6 else 1
            self.vision[2] = dist_min_top/SCREEN_WIDTH if dist_min_top != 1e6 else 1

        else:
            self.vision[0] = 1
            self.vision[1] = 1
            self.vision[2] = 1
        self.vision[3] = self.position_y/SCREEN_HEIGHT

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
