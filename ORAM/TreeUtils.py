from Bucket import Bucket


def create_perfect_tree(depth: int, bucket_capacity: int) -> list[Bucket]:
    """
    Creates a perfect binary tree with the specified depth, where each node is a Bucket.

    Parameters:
        depth (int): The depth of the binary tree. The tree will have (2^(depth + 1) - 1) nodes.
        bucket_capacity (int): The capacity for each Bucket object that represents a node in the tree.

    Returns:
        list[Bucket]: A list of Bucket objects representing the nodes of the perfect binary tree.
    """
    # Calculate the total number of nodes in the tree
    total_buckets = (1 << (depth + 1)) - 1

    # Create and return a list of Bucket objects, each initialized with the given bucket_capacity
    return [Bucket(bucket_capacity) for _ in range(total_buckets)]


def find_path_indices(leaf_pos: int, depth: int) -> list[int]:
    """
    Finds the indices of nodes along the path from a given leaf node to the root node in a perfect binary tree.

    Parameters:
        leaf_pos (int): The position of the leaf node, ranging from 0 to (2^depth - 1).
        depth (int): The depth of the binary tree. It is used to calculate the "flattened" index of the leaf node.

    Returns:
        list[int]: A list of indices representing the path from the given leaf node to the root node,
                   in order from root to leaf.
    """
    # Calculate the flattened index of the leaf node
    flat_index = (1 << depth) - 1 + leaf_pos  # Starting at leaf node position

    # Initialize an empty list to store the path indices
    path_indices = []

    # Traverse up the tree until we reach the root (index 0)
    while flat_index >= 0:
        path_indices.append(flat_index)  # Add current node to the path
        flat_index = (flat_index - 1) // 2  # Move to the parent node

    # Return the path from root to leaf by reversing the list
    return path_indices[::-1]
