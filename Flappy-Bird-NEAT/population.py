from player import Player
from species import Species
from numpy.random import randint

class Population:
    def __init__(self, size):
        self.pop = []
        self.best_score = 0
        self.innovation_history = []
        self.gen_players = []
        self.species = []
        #self.game = game
        self.gen = 0
        self.generations_since_best_score= 0
        self.population_life = 0
        self.size = size

        for i in range(self.size):
            self.pop.append(Player(230, randint(200,400)))
            self.pop[i].brain.generate_network()
            self.pop[i].brain.mutate(self.innovation_history)

    def increment_score_by_n(self, number):
            for player in self.pop:
                if player.dead == False:
                    player.increment_score_by(number)

    def check_colision_with_pipe(self, pipe, win):
            for player in self.pop:
                if pipe.collide(player, win):
                    player.dead = True

    def update_alive(self, pipes, pipe_ind, FLOOR):
        self.population_life += 1

        for player in self.pop:
            if player.y + player.img.get_height() - 10 >= FLOOR or player.y < -50:
                player.dead = True

        for player in self.pop:
            if player.dead == False:
                player.move()
                player.look(pipes, pipe_ind)
                player.think_and_act()

    def done(self):
        for player in self.pop:
            if not player.dead:
                return False
        return True

    def set_best_player(self):
        temp_best = self.species[0].players[0]
        temp_best.gen = self.gen

        if temp_best.score > self.best_score:
            self.gen_players.append(temp_best.clone())
            self.best_score = temp_best.score
            self.best_player = temp_best.clone()
            self.generations_since_best_score = 0
        else:
            self.generations_since_best_score += 1

    def natural_selection(self):
        self.speciate()
        self.calculate_fitness()
        self.sort_species()
        self.cull_species()
        self.kill_stale_species()
        self.kill_bad_species()
        self.set_best_player()
        if self.generations_since_best_score > 20:
            self.sudden_death()
        average_sum = self.get_average_fitness_sum()
        children = []

        # Get this generation's offspring
        for species in self.species:
            if len(species.players) != 0:
                # Get babies in quantity proportional to a species's fitness
                children.append(species.champ.clone())
                number_of_children = int((species.average_fitness
                                          / average_sum)
                                          * self.size)
                for i in range(number_of_children):
                    children.append(species.get_baby(self.innovation_history))

        for species in self.species:
            # If we couldn't get enough babies, grab the rest from best species
            if len(species.players) != 0:
                while len(children) < self.size:
                    children.append(species.get_baby(self.innovation_history))
                break
        
        self.pop = children.copy()
        self.gen += 1
        for player in self.pop:
            player.brain.generate_network()
        self.population_life = 0

    def speciate(self):
        for species in self.species:
            species.players = []

        for player in self.pop:
            species_found = False
            for species in self.species:
                if species.same_species(player.brain) == True:
                    species.add_to_species(player)
                    player.color = species.color
                    species_found = True
                    break
            if species_found == False:
                self.species.append(Species(player))
                player.color = self.species[-1].color

    def calculate_fitness(self):
        for player in self.pop:
            player.calculate_fitness()

    def sort_species(self):
        for species in self.species:
            species.sort_species()

        self.species.sort(key=lambda x: x.best_fitness, reverse=True)

    def kill_stale_species(self):
        """Kill species that haven't improved in a while."""
        self.species[2:] = [species for species in self.species[2:]
                           if species.staleness < 15]
    
    def kill_bad_species(self):
        """Kill species that wouldn't be able to reproduce."""
        average_sum = self.get_average_fitness_sum()

        self.species[1:] = [species for species in self.species[1:]
                           if (species.average_fitness / average_sum) *
                           self.size >= 1]

    def cull_species(self):
        """Kill bottom half players of species."""
        for species in self.species:
            species.cull()
            species.fitness_sharing()
            species.set_average()

    def sudden_death(self):
        """Kill every species but the top two if things get stale."""
        del self.species[2:]
        self.generations_since_best_score = 0

    def get_average_fitness_sum(self):
        average_sum = 0

        for species in self.species:
            if len(species.players) != 0:
                average_sum += species.average_fitness

        return average_sum