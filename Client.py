from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class Client:
    def __init__(self):
        self.__key = get_random_bytes(16)
        self.__cipher = AES.new(self.__key, AES.MODE_GCM)
        self.__memory = dict()


    def store_data(self, server, id, data):
        pass

    def retrieve_data(self, server, id):
        pass

    def delete_data(self, server, id, data):
        pass