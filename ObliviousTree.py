from ObliviousNode import ObliviousNode
import math


class ObliviousTree:
    """
    A complete binary tree designed for oblivious data storage and access.
    This structure supports hiding access patterns via reshuffling and dummy entries.
    """
    def __init__(self, capacity=4):
        self.total_nodes = self._adjust_even_size(capacity + 1)
        self.depth = int(math.log2(self.total_nodes))

        # create root, insert it and define root node of the tree
        root = ObliviousNode()
        self._tree = [[root]]
        self._root_node = root

        self._construct_levels()
        self.leaf_nodes = self._tree[-1]

    def _adjust_even_size(self, n):
        """
        Ensures the number of nodes is a power of two by rounding up.
        :param n: Desired number of data blocks + 1
        :return: Next power of two (ensures complete binary tree)
        """
        return 1 << (n - 1).bit_length()

    @staticmethod
    def _calculate_tree_depth(total_leaves):
        """
        Calculate depth needed to accommodate the number of leaves.
        """
        return math.ceil(math.log2(total_leaves))

    def _construct_levels(self):
        """
        Constructs the binary tree structure level by level.
        """
        for tree_lvl in range(self.depth - 1):
            current_row = self._tree[tree_lvl]
            next_row = []

            for node in current_row:
                left = ObliviousNode(parent=node)
                right = ObliviousNode(parent=node)

                node.left = left   # match your ObliviousNode's field names
                node.right = right

                next_row.extend([left, right])

            self._tree.append(next_row)


    def print_tree(self):
        """
        Prints the binary tree level by level.
        Each node is represented by its memory ID or data (if set).
        """
        print("ObliviousTree Structure:")
        for level_index, level_nodes in enumerate(self._tree):
            line = f"Level {level_index}: "
            for node in level_nodes:
                label = f"{id(node)}"
                if hasattr(node, 'data') and node.data is not None:
                    label += f"({node.data})"
                line += f"{label}  "
            print(line)

    def get_root(self):
        return self._root_node


    def get_node(self, level, index_node):
        return self._tree[level][index_node]

    def get_size(self, level):
        """
        Returns the number of nodes at the given tree level.
        Raises IndexError if the level is invalid.
        """
        if level < 0 or level >= len(self._tree):
            raise IndexError(f"Level {level} is out of bounds.")
        return len(self._tree[level])




#
# if __name__ == "__main__":
#     # Create a tree with 5 data elements (will be adjusted to next power of 2 internally)
#     tree = ObliviousTree(capacity=5)
#
#     # Print the tree structure
#     tree.print_tree()