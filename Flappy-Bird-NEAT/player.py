import pygame
import os
from genome import Genome
from random import randint


class Player:
    MAX_ROTATION = 25
    IMGS = [pygame.transform.scale2x(pygame.image.load(
        os.path.join("imgs", "bird" + str(x) + ".png"))) for x in range(1, 4)]
    ROT_VEL = 20
    ANIMATION_TIME = 5
    genome_inputs = 3 # Flappy-Bird Vision! If you change vision parameter in look(), change here too!
    genome_outputs = 1 # To jump or not to jump!

    def __init__(self, x, y):
        self.dead = False
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
        self.fitness = 1
        self.unadjusted_fitness = 0
        self.lifespan = 0
        self.best_score = 0
        #self.replay = False
        self.score = 1
        #self.gen = 0
        self.vision = [0 for _ in range(self.genome_inputs)]
        self.decision = 0
        self.brain = Genome(self.genome_inputs, self.genome_outputs)

    def draw(self, win):
        self.img_count += 1

        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        self.blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def blitRotateCenter(self, surf, image, topleft, angle):
       	rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(
        	center=image.get_rect(topleft=topleft).center)
        surf.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel*(self.tick_count) + 0.5 * \
            (3)*(self.tick_count)**2  

        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def clone(self):
        clone = Player(230, randint(200,400))
        clone.brain = self.brain.clone()
        clone.fitness = self.fitness
        clone.unadjusted_fitness = self.unadjusted_fitness
        clone.brain.generate_network()
        clone.best_score = self.best_score

        return clone

    def calculate_fitness(self):
        self.unadjusted_fitness = self.score*self.score
        self.fitness = self.unadjusted_fitness

    def crossover(self, parent_2):
        child = Player(230, randint(200,400))
        child.brain = self.brain.crossover(parent_2.brain)
        child.brain.generate_network()
        
        return child

    def look(self, pipes, pipe_ind):
        self.vision[0] = self.y
        self.vision[1] = abs(self.y - pipes[pipe_ind].height)
        self.vision[2] = abs(self.y - pipes[pipe_ind].bottom)

    def think_and_act(self):
        decision = self.brain.feed_forward(self.vision)[0]

        if decision > 0:
            self.jump()

    #def increment_counters(self):
    #    self.lifespan += 1
#
     #   if self.lifespan % 5 == 0:
      #      self.score += 1

    def increment_score_by(self, number):
        self.score += number