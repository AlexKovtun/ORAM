from TreeUtils import create_perfect_tree, find_path_indices


class Server:
    """
    ORAM Server that stores a binary tree of buckets and provides
    path-based read/write operations.
    """

    def __init__(self, depth: int, bucket_capacity: int):
        # Initialize tree with given depth and bucket capacity
        self._depth = depth
        self._bucket_capacity = bucket_capacity
        self._tree = create_perfect_tree(depth, bucket_capacity)

    def read_path(self, leaf_index: int):
        """
        Read all blocks along the path from root to given leaf.

        Args:
            leaf_index (int): Index of the target leaf node.

        Returns:
            list: Blocks collected along the path.
        """
        path = find_path_indices(leaf_index, self._depth)
        collected_blocks = []
        for node_index in path:
            collected_blocks += self._tree[node_index].get_blocks()
        return collected_blocks

    def write_path(self, leaf_index: int, blocks: list):
        """
        Write blocks along the path from root to given leaf, filling each bucket up to capacity.

        Args:
            leaf_index (int): Index of the target leaf node.
            blocks (list): Blocks to write along the path.
        """
        path = find_path_indices(leaf_index, self._depth)
        current = 0

        for node_index in path:
            bucket = self._tree[node_index]
            bucket.reset_content()
            capacity = self._bucket_capacity

            for _ in range(capacity):
                if current >= len(blocks):
                    break
                bucket.add_block(blocks[current])
                current += 1