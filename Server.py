import ObliviousTree

BUCKET_SIZE = 4  # Optional: move to config later


class Server:
    def __init__(self, num_blocks):
        self._tree = ObliviousTree.ObliviousTree(num_blocks)
        self.bucket_size = BUCKET_SIZE
        self.max_depth = self._tree.depth

    def get_root(self):
        return self._tree.get_root()

    def get_node(self, level, i):
        """
        Returns the i-th node at the given level.
        """
        if level < 0 or level >= self.max_depth:
            raise IndexError(f"Level {level} is out of bounds.")

        if i < 0 or i >= self._tree.get_size(level):
            raise IndexError(f"Index {i} is out of bounds at level {level}.")

        return self._tree.get_node(level, i)

    def get_leaf(self, i):
        """
        Returns the i-th leaf node.
        """
        if i < 0 or i >= self._tree.get_size(self.max_depth):
            raise IndexError(f"Leaf index {i} is out of bounds.")
        return self._tree.leaf_nodes[i]

    def print_tree(self):
        """
        Print the underlying tree.
        """
        self._tree.print_tree()
