from Block import Block

class Bucket:
    def __init__(self, capacity: int):
        """
        Initializes the Bucket with a given capacity.

        Args:
            capacity (int): The maximum number of blocks the bucket can hold.
        """
        self._capacity = capacity
        self._blocks = []

    def __repr__(self):
        return f" --Bucket({self._blocks})"

    # Getter and Setter for _capacity
    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value: int):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Capacity must be a positive integer.")
        self._capacity = value
        # Ensure we don't exceed the new capacity, truncate blocks if needed
        if len(self._blocks) > self._capacity:
            self._blocks = self._blocks[:self._capacity]

    # Getter for _blocks (read-only)
    @property
    def blocks(self):
        return self._blocks.copy()

    # Method to add a block to the bucket
    def add_block(self, block: Block):
        if len(self._blocks) < self._capacity:
            self._blocks.append(block)
        else:
            raise Exception("Reached max capacity")

    # Method to reset the content of the bucket
    def reset_content(self):
        self._blocks = []

    # Method to get all blocks in the bucket
    def get_blocks(self):
        return self._blocks.copy()

