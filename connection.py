from random import uniform, gauss

class Connection:
    def __init__(self, from_node, to_node, weight, innovation_number):
        self.from_node = from_node
        self.to_node = to_node
        self.weight = weight
        self.innovation_number = innovation_number
        self.enabled = True

    def mutate_weight(self):
        p_mutation = uniform(0, 1)

        if p_mutation < 0.1:
            self.weight = uniform(-1, 1)
        else:
            self.weight += gauss(0, 1/100)
            if self.weight > 1:
                self.weight = 1
            elif self.weight < 1:
                self.weight = -1

    def clone(self, from_node, to_node):
        clone = Connection(from_node, to_node, self.weight, self.innovation_number)
        clone.enabled = True

        return clone
