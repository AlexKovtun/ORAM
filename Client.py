import json
import random
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
from Crypto.Random import get_random_bytes

DUM_VAL = '0000'
DUMMY_LEN = 5

class Client:
    """
    Class represents a client.
    """
    def __init__(self):
        """
        Initialize the memory and encryption key of the client.
        All fields should be super private.
        """
        self.__memory = dict()
        self.__key = get_random_bytes(16)


    def _fill_server_with_dummies(self, server):
        for level in range(server.height + 1):
            for j in range(server.num_nodes_in_level(level)):
                node = server.get_node_in_level(level, j)
                node.value = dict()
                for i in range(server.bucket_size):
                    dummy_key = self._encrypt(Client.get_random_string(DUMMY_LEN).encode())
                    dummy_val = self._encrypt(b'0000')
                    node.value[dummy_key] = dummy_val



    def _encrypt(self, plaintext, header=b"header"):
        cipher = AES.new(self.__key, AES.MODE_GCM)
        cipher.update(header)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        return {
            'nonce': cipher.nonce,
            'header': header,
            'ciphertext': ciphertext,
            'tag': tag
        }

    def _decrypt(self, enc_data):
        cipher = AES.new(self.__key, AES.MODE_GCM, nonce=enc_data['nonce'])
        cipher.update(enc_data['header'])
        return cipher.decrypt_and_verify(enc_data['ciphertext'], enc_data['tag'])

    def _encrypt_node(self, node):
        new_dict = dict()
        for key in node.value:
            dec_key = self._decrypt(key).decode()
            dec_val = self._decrypt(node.value[key]).decode()
            new_key = self._encrypt(dec_key.encode())
            new_val = self._encrypt(dec_val.encode())
            new_dict[new_key] = new_val
        node.value = new_dict

    def store_data(self, server, id, data):
        if id in self.__memory:
            return 'ID already exists. Please delete it first'

        root = server.get_root()
        if root.value is None:
            self._fill_server_with_dummies(server)

        hmac = HMAC.new(self.__key, digestmod=SHA256)
        hmac.update(str(id).encode() + data.encode())
        self.__memory[id] = [bin(random.randint(server.leaf_min, server.leaf_max))[2:],
                             hmac.hexdigest()] #TODO: change this leaf min and max

        for key in list(root.value.keys()):
            dec_key = self._decrypt(root.value[key]).decode()
            if dec_key == DUM_VAL:
                del root.value[key]
                enc_id = self._encrypt(str(id).encode())
                enc_data = self._encrypt(('1' + data).encode())
                root.value[enc_id] = enc_data
                self._encrypt_node(root)
                break

        self._push_down(server)

    def _push_down(self, server):
        for level in range(server.height + 1):
            if level == server.height:
                return
            if level == 0:
                self._rand_and_push(server.get_root(), server, level)
            else:
                rand1 = random.randint(0, server.num_nodes_in_level(level)-1)
                rand2 = random.randint(0, server.num_nodes_in_level(level)-1)
                while rand1 == rand2:
                    rand2 = random.randint(0, server.num_nodes_in_level(level)-1)
                node1 = server.get_node_in_level(level, rand1)
                node2 = server.get_node_in_level(level, rand2)
                for s_node in [node1, node2]:
                    self._rand_and_push(s_node, server, level)

    def _rand_and_push(self, node, server, level):
        """
        Randomize 2 different elements in a node and push them to the next level.
        :param node: Node object to pick elements from.
        :param server: Server object which contains the node.
        :param level: Current level of pushing.
        """
        keys = list(node.value.keys())
        if len(keys) < 2:
            return  # Not enough data to push

        rand1 = random.randint(0, len(keys) - 1)
        rand2 = random.randint(0, len(keys) - 1)
        while rand1 == rand2: # Verify we don't have 2 same keys
            rand2 = random.randint(0, len(keys) - 1)

        key1= keys[rand1]
        data1 = node.value[key1]

        key2 = keys[rand2]
        data2 = node.value[key2]

        self._push_selected_data(key1, data1, node, level)
        self._push_selected_data(key2, data2, node, level)

    def _push_selected_data(self, key, data, prev_node, level):
        """
        Pushes key and data to the next node in the path to their leaf.
        :param key: bytes, encrypted ID.
        :param data: bytes, encrypted payload.
        :param prev_node: Node object containing the given data.
        :param level: Current level of pushing.
        """
        dec_key = self._decrypt(key).decode()
        dec_data = self._decrypt(data)

        if dec_data[0:1] == b'0':  # Dummy
            direction = random.randint(0, 1)
        else:
            direction_bit_str = self.__memory[int(dec_key)][0]
            if level >= len(direction_bit_str):
                # Fallback if out of bounds
                direction = random.randint(0, 1)
            else:
                direction = int(direction_bit_str[level])

        next_node = prev_node.left if direction == 0 else prev_node.right

        # Remove the current entry and replace with dummy
        del prev_node.value[key]
        dummy_key = self._encrypt(Client.get_random_string(DUMMY_LEN).encode())
        dummy_val = self._encrypt(b'00000')
        prev_node.value[dummy_key] = dummy_val

        # Try to replace a dummy in the next node
        for cur_key in list(next_node.value.keys()):
            dec_val = self._decrypt(next_node.value[cur_key])
            if dec_val[0:1] == b'0':  # Dummy
                del next_node.value[cur_key]
                next_node.value[key] = data
                return




    @staticmethod
    def get_random_string(length):
        return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
