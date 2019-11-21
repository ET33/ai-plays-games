from player import Player
from species import Species

class Population:
    def __init__(self, size, enemy_list):
        self.pop = []
        self.best_score = 0
        self.innovation_history = []
        self.gen_players = []
        self.species = []
        self.enemy_list = enemy_list
        self.gen = 0

        self.mass_extinction_event = False
        self.new_stage = False
        self.population_life = 0

        for i in range(size):
            self.pop.append(Player(self.enemy_list))
            self.pop[i].brain.generate_network()
            self.pop[i].brain.mutate(self.innovation_history)

    def update_alive(self):
        self.population_life += 1

        for player in self.pop:
            if player.dead == False:
                player.look()
                player.think()
                player.update()

    def done(self):
        for player in self.pop:
            if player.dead == False:
                return False

        return True

    def set_best_player(self):
        temp_best = self.species[0].players[0]
        temp_best.gen = self.gen

        if temp_best.score > self.best_score:
            self.gen_players.append(temp_best.clone())
            self.best_score = temp_best.score
            self.best_player = temp_best.clone()

    def natural_selection(self):
        self.speciate()
        self.calculate_fitness()
        self.sort_species()

        if self.mass_extinction_event == True:
            self.mass_extinction()
            self.mass_extinction_event = False

        self.cull_species()
        self.set_best_player()
        self.kill_stale_species()
        self.kill_bad_species()

        average_sum = self.get_average_fitness_sum()
        children = []

        for species in self.species:
            children.append(species.champ.clone())

            number_of_children = int(species.average_fitness/average_sum * len(self.pop))-1
            for i in range(number_of_children):
                children.append(species.get_baby(self.innovation_history))

        while len(children) < len(self.pop):
            children.append(self.species[0].get_baby(self.innovation_history))
        
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
        self.species[2:] = [species for species in self.species[2:]
                           if species.staleness < 15]
    
    def kill_bad_species(self):
        average_sum = self.get_average_fitness_sum()

        self.species[1:] = [species for species in self.species[1:]
                           if species.average_fitness/average_sum *
                           len(self.pop) >= 1]

    def cull_species(self):
        for species in self.species:
            species.cull()
            species.fitness_sharing()
            species.set_average()

    def mass_extinction(self):
        del self.species[5:]

    def get_average_fitness_sum(self):
        average_sum = 0

        for species in self.species:
            average_sum += species.average_fitness

        return average_sum
