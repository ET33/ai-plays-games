class ConnectionHistory:
    global_innovation_number = 1

    def __init__(self, from_node, to_node):
        self.from_node = from_node
        self.to_node = to_node
        self.innovation_number = ConnectionHistory.global_innovation_number
        ConnectionHistory.global_innovation_number += 1

    def matches(self, from_node, to_node):
        if (from_node.number == self.from_node
                and to_node.number == self.to_node):
            return True
        return False
