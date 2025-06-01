class Block:
    """
    Represents a data block in the ORAM tree.

    Attributes:
        _id (int): Identifier of the block (can be None for dummy blocks).
        data (str): 4-character string containing the block's data.
        _is_dummy (bool): Indicates if the block is a dummy (used to hide real data).
    """

    def __init__(self, block_id=None, data=None, is_dummy=True):
        self._id = block_id
        self._is_dummy = is_dummy

        self._tag = None
        self._nonce = None
        self._ciphertext = None

        # Set the data if not a dummy block and data has exactly 3 elements
        if not self._is_dummy and data is not None and len(data) == 3:
            self._nonce, self._ciphertext, self._tag = data


    # Getter for block id
    @property
    def id(self):
        return self._id

    # Setter for block id
    @id.setter
    def id(self, value):
        if value is not None and not isinstance(value, int):
            raise ValueError("Block ID must be an integer.")
        self._id = value

    # Getter for is_dummy flag
    @property
    def is_dummy(self):
        return self._is_dummy


    # Getter for the full data tuple
    @property
    def data(self):
        if self._is_dummy:
            return None
        return (self._nonce, self._ciphertext, self._tag)

    # Setter for full data (nonce, ciphertext, tag)
    @data.setter
    def data(self, value):
        if value is not None and isinstance(value, tuple) and len(value) == 3:
            self._nonce, self._ciphertext, self._tag = value
        else:
            raise ValueError("Data must be a tuple with 3 elements (nonce, ciphertext, tag).")


    def __repr__(self):
        if self._is_dummy:
            return f"Block(dummy)"
        return f"Block(id={self._id})"