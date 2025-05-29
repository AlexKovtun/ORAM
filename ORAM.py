import random
import math
from typing import Optional, List, Tuple, Dict


class Block:
    def __init__(self, block_id: int, data: str, leaf: int):
        self.block_id = block_id
        self.data = data
        self.leaf = leaf  # the leaf this block is assigned to

    def __repr__(self):
        return f"Block(id={self.block_id}, data={self.data}, leaf={self.leaf})"


class Server:
    def __init__(self, num_blocks: int, Z: int = 4):
        self.num_blocks = num_blocks
        self.Z = Z
        self.tree_height = math.ceil(math.log2(num_blocks))
        self.leaf_count = 2 ** self.tree_height
        self.buckets: Dict[Tuple[int, int], List[Block]] = {}  # (depth, index) -> List[Block]

        for depth in range(self.tree_height + 1):
            for index in range(2 ** depth):
                self.buckets[(depth, index)] = []

    def get_bucket(self, depth: int, index: int) -> List[Block]:
        return self.buckets[(depth, index)]

    def set_bucket(self, depth: int, index: int, blocks: List[Block]):
        self.buckets[(depth, index)] = blocks[:self.Z]  # enforce bucket capacity

    def read_path(self, leaf: int) -> List[Block]:
        path = []
        for depth in range(self.tree_height + 1):
            index = leaf >> (self.tree_height - depth)
            path.extend(self.get_bucket(depth, index))
        return path

    def write_path(self, leaf: int, blocks: List[Block]):
        levels = range(self.tree_height, -1, -1)
        for depth in levels:
            index = leaf >> (self.tree_height - depth)
            eligible_blocks = [b for b in blocks if (b.leaf >> (self.tree_height - depth)) == index]
            to_write = eligible_blocks[:self.Z]
            self.set_bucket(depth, index, to_write)
            blocks = [b for b in blocks if b not in to_write]  # remove written blocks

    def print_tree(self):
        print("ORAM Tree Structure:")
        for depth in range(self.tree_height + 1):
            for index in range(2 ** depth):
                bucket = self.get_bucket(depth, index)
                print(f"Level {depth}, Bucket {index}: {bucket}")

class Client:
    def __init__(self, num_blocks: int):
        self.position_map: Dict[int, int] = {}  # block_id -> leaf
        self.stash: Dict[int, Block] = {}  # block_id -> Block, bounded by O(num_blocks)
        self.num_blocks = num_blocks
        self.tree_height = math.ceil(math.log2(num_blocks))
        self.leaf_count = 2 ** self.tree_height

    def get_random_leaf(self) -> int:
        return random.randint(0, self.leaf_count - 1)

    def store_data(self, server: Server, block_id: int, data: str):
        leaf = self.get_random_leaf()
        self.position_map[block_id] = leaf
        self._access(server, block_id, data)

    def retrieve_data(self, server: Server, block_id: int) -> Optional[str]:
        result = self._access(server, block_id, None)
        return result

    def delete_data(self, server: Server, block_id: int):
        self._access(server, block_id, "__DELETE__")

    def _access(self, server: Server, block_id: int, data: Optional[str]) -> Optional[str]:
        if block_id not in self.position_map:
            return None

        old_leaf = self.position_map[block_id]
        new_leaf = self.get_random_leaf()
        self.position_map[block_id] = new_leaf

        # Step 1: Read path and add to stash
        path_blocks = server.read_path(old_leaf)
        for block in path_blocks:
            self.stash[block.block_id] = block

        # Step 2: Update or retrieve
        result = None
        if block_id in self.stash:
            block = self.stash[block_id]
            if data == "__DELETE__":
                del self.stash[block_id]
            elif data is not None:
                block.data = data
                block.leaf = new_leaf
            result = block.data
        elif data is not None and data != "__DELETE__":
            self.stash[block_id] = Block(block_id, data, new_leaf)

        # Step 3: Write back from stash along path (bottom to top)
        blocks_to_write = list(self.stash.values())
        server.write_path(old_leaf, blocks_to_write)

        # Remove blocks that were successfully placed
        remaining_stash = {}
        for block in self.stash.values():
            if not self._can_place_on_path(block, old_leaf):
                remaining_stash[block.block_id] = block
        self.stash = remaining_stash

        return result

    def _can_place_on_path(self, block: Block, leaf: int) -> bool:
        for d in range(self.tree_height + 1):
            if (block.leaf >> (self.tree_height - d)) != (leaf >> (self.tree_height - d)):
                return False
        return True



if __name__ == "__main__":
    # Initialize server and client
    num_blocks = 8  # Number of data blocks the server can store
    server = Server(num_blocks)
    client = Client(num_blocks)

    # Store some data
    client.store_data(server, 1, "AAAA")
    client.store_data(server, 2, "BBBB")
    client.store_data(server, 3, "CCCC")

    # Retrieve data
    print("Retrieve ID 1:", client.retrieve_data(server, 1))
    print("Retrieve ID 2:", client.retrieve_data(server, 2))

    # Update a block
    client.store_data(server, 1, "ZZZZ")
    print("Retrieve updated ID 1:", client.retrieve_data(server, 1))

    # Delete a block
    client.delete_data(server, 2)
    print("Retrieve deleted ID 2:", client.retrieve_data(server, 2))

    # Final tree printout
    print("\nFinal ORAM Tree:")
    server.print_tree()