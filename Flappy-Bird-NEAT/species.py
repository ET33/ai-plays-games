from random import uniform, randrange

class Species:
    def __init__(self, player=None):
        self.players = []
        self.best_fitness = 0
        self.average_fitness = 0
        self.staleness = 0
        self.excess_coeff = 1
        self.weight_diff_coeff = 0.4
        self.compatibility_threshold = 3
        self.color = (randrange(256),
                      randrange(256),
                      randrange(256))

        if player != None:
            self.players.append(player)
            self.best_fitness = player.fitness
            self.rep = player.brain.clone()
            self.champ = player.clone()

    def same_species(self, genome):
        excess_and_disjoint = self.get_excess_disjoint(genome, self.rep)
        average_weight_diff = self.average_weight_diff(genome, self.rep)

        normaliser = max(len(genome.genes), len(self.rep.genes))
        if normaliser <= 20:
            normaliser = 1

        compatibility = (self.excess_coeff * excess_and_disjoint
                         / normaliser
                         + self.weight_diff_coeff * average_weight_diff)
        return self.compatibility_threshold > compatibility

    def add_to_species(self, player):
        self.players.append(player)

    def get_excess_disjoint(self, genome_1, genome_2):
        matching = 0

        for gene_1 in genome_1.genes:
            for gene_2 in genome_2.genes:
                if gene_1.innovation_number == gene_2.innovation_number:
                    matching += 1
                    break

        return len(genome_1.genes) + len(genome_2.genes) - 2*matching

    def average_weight_diff(self, genome_1, genome_2):
        if len(genome_1.genes) == 0 or len(genome_2.genes) == 0:
            return 0

        matching = 0
        total_diff = 0

        for gene_1 in genome_1.genes:
            for gene_2 in genome_2.genes:
                if gene_1.innovation_number == gene_2.innovation_number:
                    matching += 1
                    total_diff += abs(gene_1.weight-gene_2.weight)
                    break
        if matching == 0:
            return 0

        return total_diff/matching

    def sort_species(self):
        if len(self.players) == 0:
            self.staleness += 1
            return
        self.players.sort(key=lambda x: x.fitness, reverse=True)

        if self.players[0].fitness > self.best_fitness:
            self.staleness = 0
            self.best_fitness = self.players[0].fitness
            self.rep = self.players[0].brain.clone()
            self.champ = self.players[0].clone()
        else:
            self.staleness += 1

    def set_average(self):
        if len(self.players) == 0:
            return

        fitness_sum = 0

        for player in self.players:
            fitness_sum += player.fitness

        self.average_fitness = fitness_sum/len(self.players)

    def get_baby(self, innovation_history):
        p = uniform(0,1)

        if p < 0.25:
            # Get a baby with no crossover
            baby = self.select_player().clone()
        else:
            # Perform the crossover between parents
            parent_1 = self.select_player()
            parent_2 = self.select_player()

            # Inherit excessive/disjoint genes from fittest parent
            if parent_1.fitness < parent_2.fitness:
                baby = parent_2.crossover(parent_1)
            else:
                baby = parent_1.crossover(parent_2)

        # Mutate baby
        baby.brain.mutate(innovation_history)
        return baby

    def select_player(self):
        fitness_sum = 0

        for player in self.players:
            fitness_sum += player.fitness

        p  = uniform(0, fitness_sum)
        running_sum = 0

        for player in self.players:
            running_sum += player.fitness
            if running_sum >= p:
                return player

    def cull(self):
        """Culls bottom half of the species."""
        if len(self.players) > 2:
            del self.players[len(self.players)//2:]

    def fitness_sharing(self):
        for player in self.players:
            player.fitness = player.unadjusted_fitness / len(self.players)