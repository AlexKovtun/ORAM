import random
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

from TreeUtils import find_path_indices
from Block import Block

# OPERATIONS WE CAN DO
OP_WRITE = "write"
OP_READ = "read"
OP_DELETE = "delete"

# CONSTANTS
AES_KEY_SIZE = 16

class Client:
    """
    ORAM client managing encrypted access with a stash and position map.
    """

    def __init__(self, tree_height: int):
        self._key = get_random_bytes(AES_KEY_SIZE)  # Symmetric key for AES encryption
        self._depth = tree_height  # Height of the ORAM tree
        self._pos_map = {}  # Maps block ID to a leaf index
        self._stash = []  # Temporary storage for blocks

    def _decrypt_block(self, nonce: bytes, cipher_text: bytes, tag: bytes) -> str:
        # Decrypts and verifies a block using AES-GCM
        aes = AES.new(self._key, AES.MODE_GCM, nonce=nonce)
        return aes.decrypt_and_verify(cipher_text, tag).decode()

    def _encrypt_block(self, content: str) -> tuple[bytes, bytes, bytes]:
        # Encrypts block content using AES-GCM
        aes = AES.new(self._key, AES.MODE_GCM)
        cipher_text, tag = aes.encrypt_and_digest(content.encode())
        return aes.nonce, cipher_text, tag

    def _assign_new_leaf(self) -> int:
        # Randomly assigns a new leaf index
        return random.randrange(2 ** self._depth)

    def _flush_to_tree(self, server, indices: list[int], used_ids: set, valid_indices: set, output_blocks: list):
        # Evicts blocks from stash back to ORAM path
        for _ in indices:
            group = []
            for block in self._stash:
                if len(group) >= server._bucket_capacity:
                    break
                if block._id not in used_ids and self._pos_map.get(block._id) in valid_indices:
                    group.append(block)
                    used_ids.add(block._id)
            output_blocks.extend(group)

    def _handle_access(self, block_id: int, action: str, payload: str | None, stash_snapshot: list[Block]):
        # Handles read/write/delete operation on stash
        outcome = None
        new_stash = []
        located = False

        for block_from_stash in stash_snapshot:
            if block_from_stash.is_dummy or block_from_stash._id != block_id:
                new_stash.append(block_from_stash)
                continue

            located = True
            if action == OP_READ:
                try:
                    outcome = self._decrypt_block(
                        block_from_stash._nonce,
                        block_from_stash._ciphertext,
                        block_from_stash._tag
                    )
                except Exception as err:
                    raise ValueError(f"Failed to decrypt block {block_id}: {err}")
                new_stash.append(block_from_stash)
            elif action == OP_WRITE:
                new_stash.append(Block(block_id, self._encrypt_block(payload), is_dummy=False))
            elif action == OP_DELETE:
                continue  # Skip adding this block

        if action == OP_WRITE and not located:
            new_stash.append(Block(block_id, self._encrypt_block(payload), is_dummy=False))

        return outcome, new_stash, located

    def _process_request(self, server, block_id: int, action: str, payload: str = None):
        # Main handler for read/write/delete requests
        if block_id not in self._pos_map:
            self._pos_map[block_id] = self._assign_new_leaf()
        leaf = self._pos_map[block_id]

        path_idxs = find_path_indices(leaf, self._depth)
        fetched_blocks = server.read_path(leaf)
        self._stash.extend(fetched_blocks)

        result, self._stash, _ = self._handle_access(block_id, action, payload, self._stash)

        self._pos_map[block_id] = self._assign_new_leaf()  # Re-assign position

        targets = set(path_idxs)
        used = set()
        to_evict = []

        self._flush_to_tree(server, path_idxs, used, targets, to_evict)

        self._stash = [block for block in self._stash if block._id not in used]

        server.write_path(leaf, to_evict)
        return result

    def retrieve_data(self, server, block_id: int):
        # Retrieves and decrypts data from the server
        return self._process_request(server, block_id, OP_READ)

    def store_data(self, server, block_id: int, content: str):
        # Stores encrypted data on the server
        self._process_request(server, block_id, OP_WRITE, content)

    def delete_data(self, server, block_id: int):
        # Deletes data from ORAM
        self._process_request(server, block_id, OP_DELETE)\

