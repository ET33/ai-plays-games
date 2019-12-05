"""A Neuroevolution of Augmenting Topologies (NEAT) method implementation for
training neural networks to play games.
"""

import pygame
import random
import os
import time
import pickle
from player import Player
from pipe import Pipe
from floor import Floor
from population import Population
pygame.font.init()

WIN_WIDTH = 600
WIN_HEIGHT = 800
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False
MAX_GENERATIONS = 50
POP_SIZE = 10
pygame.display.set_caption("Flappy Bird")
gen = 1
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))


def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        if bird.dead == False:
            if DRAW_LINES:
                try:
                    pygame.draw.line(win, (255, 0, 0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height(
                    )/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                    pygame.draw.line(win, (255, 0, 0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height(
                    )/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
                except:
                    pass
            bird.draw(win)

    score_label = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    score_label = STAT_FONT.render(
        "Generation: " + str(gen-1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    birds_alive = count_alive(birds)
    score_label = STAT_FONT.render(
        "Alive: " + str(birds_alive), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def count_alive(pop):
    count = 0
    for bird in pop:
        if bird.dead == False:
            count += 1
    return count

def eval_genomes(pop):
    global WIN

    clock = pygame.time.Clock()
    pipes = [Pipe(700)]
    base = Floor(FLOOR)
    win = WIN
    score = 0

    run = True
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            pop.check_colision_with_pipe(pipe, win)
        
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < pop.pop[0].x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            pop.increment_score_by_n(10)
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        pipe_ind = 0
        if pop.done() != True:
            if len(pipes) > 1 and pop.pop[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
            pop.increment_score_by_n(0.03)
            pop.update_alive(pipes, pipe_ind, FLOOR)
            base.move()
        else:
            pop.natural_selection()
            run = False

        draw_window(WIN, pop.pop, pipes, base, score, gen, pipe_ind)

def main():
    pop = Population(POP_SIZE)
    global gen
    for _ in range(MAX_GENERATIONS):
        eval_genomes(pop)
        gen += 1

if __name__ == "__main__":
    main()
