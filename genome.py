from random import randrange, uniform

from node import Node
from connection import Connection
from connection_history import ConnectionHistory

class Genome:
    def __init__(self, inputs, outputs, crossover=False):
        self.genes = []
        self.nodes = []
        self.layers = 2
        self.next_node = 0
        self.next_connection_number = 1000
        self.network = []

        self.inputs = inputs
        self.outputs = outputs
        
        if crossover == False:
            for i in range(self.inputs):
                self.nodes.append(Node(i))
                self.nodes[i].layer = 0
                self.next_node += 1

            for i in range(self.outputs):
                self.nodes.append(Node(inputs+i))
                self.nodes[inputs+i].layer = 1
                self.next_node += 1

            self.nodes.append(Node(self.next_node))
            self.nodes[self.next_node].layer = 0
            self.bias_node = self.next_node
            self.next_node += 1

    def get_node(self, number):
        for node in self.nodes:
            if number == node.number:
                return node

        return None

    def connect_nodes(self):
        for node in self.nodes:
            node.output_connection = []

        for gene in self.genes:
            gene.from_node.output_connections.append(gene)

    def feed_forward(self, input_values):
        for i in range(self.inputs):
            self.nodes[i].output_value = input_values[i]

        self.nodes[self.bias_node].output_value = 1

        for node in self.network:
            node.engage()

        output_values = []

        for i in range(self.outputs):
            output_values.append(self.nodes[self.inputs+i].output_value)

        for node in self.nodes:
            node.input_sum = 0

        return output_values

    def generate_network(self):
        self.connect_nodes()
        
        for l in range(self.layers):
            for node in self.nodes:
                if node.layer == l:
                    self.network.append(node)

    def add_node(self, innovation_history):
        if len(self.genes) == 0:
            add_connection(innovation_history)

        random_index = randrange(len(self.genes))

        tries = 0
        while (self.genes[random_index].from_node is
               self.nodes[self.bias_node]) and tries < 20:
            random_index = randrange(len(self.genes))
            tries += 1

        if self.genes[random_index].from_node is self.nodes[self.bias_node]:
            return

        self.genes[random_index].enabled = False

        new_node_index = self.next_node
        self.nodes.append(Node(new_node_index))
        self.next_node += 1

        connection_innovation_number = self.get_innovation_number(
                                       innovation_history,
                                       self.genes[random_index].from_node,
                                       self.get_node(new_node_index))
        self.genes.append(Connection(self.genes[random_index].from_node,
                                     self.get_node(new_node_index), 1,
                                     connection_innovation_number))

        connection_innovation_number = self.get_innovation_number(
                                       innovation_history,
                                       self.get_node(new_node_index),
                                       self.genes[random_index].to_node)
        self.genes.append(Connection(self.get_node(new_node_index),
                                     self.genes[random_index].to_node,
                                     self.genes[random_index].weight,
                                     connection_innovation_number))

        self.get_node(new_node_index).layer = self.genes[
                                              random_index].from_node.layer + 1

        connection_innovation_number = self.get_innovation_number(
                                       innovation_history,
                                       self.nodes[self.bias_node],
                                       self.get_node(new_node_index))
        self.genes.append(Connection(self.nodes[self.bias_node],
                                     self.get_node(new_node_index), 0,
                                     connection_innovation_number))

        if self.get_node(new_node_index).layer == self.genes[
                                                  random_index].to_node.layer:
            for node in self.nodes:
                if node is not self.get_node(new_node_index):
                    if node.layer >= self.get_node(new_node_index).layer:
                        node.layer += 1

            self.layers += 1

        self.connect_nodes()

    def add_connection(self, innovation_history):
        if self.fully_connected():
            return

        random_node_1 = randrange(len(self.nodes))
        random_node_2 = randrange(len(self.nodes))

        while self.is_connection_viable(random_node_1, random_node_2) == False:
            random_node_1 = randrange(len(self.nodes))
            random_node_2 = randrange(len(self.nodes))

        if self.nodes[random_node_1].layer > self.nodes[random_node_2].layer:
            swap = random_node_2
            random_node_2 = random_node_1
            random_node_1 = swap

        connection_innovation_number = self.get_innovation_number(
                                       innovation_history,
                                       self.nodes[random_node_1],
                                       self.nodes[random_node_2])
        self.genes.append(Connection(self.nodes[random_node_1],
                                     self.nodes[random_node_2],
                                     uniform(-1, 1),
                                     connection_innovation_number))
        self.connect_nodes()

    def is_connection_viable(self, node_1, node_2):
        if (self.nodes[node_1].layer == self.nodes[node_2].layer
            or self.nodes[node_1].is_connected(self.nodes[node_2])):
            return False

        return True

    def get_innovation_number(self, innovation_history, from_node, to_node):
        is_new = True
        connection_innovation_number = self.next_connection_number

        for innovation in innovation_history:
            if innovation.matches(self, from_node, to_node):
                is_new = False
                connection_innovation_number = innovation.innovation_number
                break

        if is_new:
            innovation_numbers = []

            for gene in self.genes:
                innovation_numbers.append(gene.innovation_number)

            innovation_history.append(ConnectionHistory(from_node.number,
                                      to_node.number,
                                      connection_innovation_number,
                                      innovation_numbers))
            self.next_connection_number += 1

        return connection_innovation_number

    def fully_connected(self):
        max_connections = 0
        nodes_in_layer = [0 for _ in range(self.layers)]

        for node in self.nodes:
            nodes_in_layer[node.layer] += 1

        for i in range(self.layers-1):
            nodes_in_next_layers = 0
            for j in range(i+1, self.layers):
                nodes_in_next_layers += nodes_in_layer[j]

            max_connections += nodes_in_layer[i] * nodes_in_next_layers

        if max_connections == len(self.genes):
            return True

        return False

    def mutate(self, innovation_history):
        if (len(self.genes) == 0):
            self.add_connection(innovation_history)
        
        p = uniform(0, 1)

        if p < 0.75:
            for gene in self.genes:
                gene.mutate_weight()

        p = uniform(0, 1)

        if p < 0.05:
            self.add_connection(innovation_history)

        p = uniform(0, 1)

        if p < 0.01:
            self.add_node(innovation_history)


    def crossover(self, parent_2):
        child = Genome(self.inputs, self.outputs, crossover=True)
        child.genes = []
        child.nodes = []
        child.layers = self.layers
        child.next_node = self.next_node
        child.bias_node = self.bias_node
        
        child_genes = []
        is_enabled = []

        for gene in self.genes:
            set_enabled = True

            parent_2_gene = self.matching_gene(parent_2,
                                               gene.innovation_number)

            if parent_2_gene is not None:
                if gene.enabled == False or parent_2_gene.enabled == False:
                    p = uniform(0, 1)

                    if p < 0.75:
                        set_enabled = False
                p = uniform(0, 1)

                if p < 0.5:
                    child_genes.append(gene)
                else:
                    child_genes.append(parent_2_gene)
            else:
                child_genes.append(gene)
                set_enabled = gene.enabled

            is_enabled.append(set_enabled)

        for node in self.nodes:
            child.nodes.append(node.clone())

        for i, gene in enumerate(child_genes):
            child.genes.append(gene.clone(
                               child.get_node(gene.from_node.number),
                               child.get_node(gene.to_node.number)))
            child.genes[i].enabled = is_enabled[i]

        child.connect_nodes()
        return child

    def matching_gene(self, parent_2, innovation_number):
        for gene in parent_2.genes:
            if gene.innovation_number == innovation_number:
                return gene

        return None

    def clone(self):
        clone = Genome(self.inputs, self.outputs, crossover=True)

        for node in self.nodes:
            clone.nodes.append(node.clone())

        for gene in self.genes:
            clone.genes.append(gene.clone(
                               clone.get_node(gene.from_node.number),
                               clone.get_node(gene.to_node.number)))

        clone.layers = self.layers
        clone.next_node = self.next_node
        clone.bias_node = self.bias_node
        clone.connect_nodes()

        return clone
