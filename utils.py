from datetime import datetime, timedelta
from PyQt5.QtCore import Qt
import string
import numpy
from random import sample
from db import queries

password = None
key_list = None
vectors = []
reg_counter = 0
password_check_sensitivity = 0.5


def check_password_complexity(password: str) -> int: #проверка сложности
    T = 30
    V = 0.1
    L = len(password)
    A = 95
    S = A ** L
    P = (V * T) / S

    return P


def generate_password( #генерация пароля
    length: int, with_uppercase=False, with_lowercase=False, with_digits=False, with_spec_chars=False
):
    chars_pool = ""
    if with_digits:
        chars_pool += string.digits
    if with_lowercase:
        chars_pool += string.ascii_lowercase
    if with_uppercase:
        chars_pool += string.ascii_uppercase
    if with_spec_chars:
        chars_pool += string.punctuation

    return ''.join(sample(chars_pool, length))


class KeyPressing:
    start_time: timedelta
    end_time: timedelta
    key: str

    def serialize(self):
        return {
            "key": self.key,
            "start": self.start_time.microseconds / 10**6 + self.start_time.seconds,
            "end": self.end_time.microseconds / 10**6 + self.end_time.seconds,
        }


class KeyList:
    start_time: datetime
    key_list: list[KeyPressing]

    def __init__(self):
        self.key_list = list()

    @staticmethod
    def key_id_to_key(key_id):
        if Qt.Key_Shift == key_id:
            return "Shift"
        if Qt.Key_Backspace == key_id:
            return "Backspace"
        return chr(key_id)

    def press(self, key_id):
        if Qt.Key_Backspace == key_id:
            if len(self.key_list) > 0 and self.key_list[-1].key != "Shift":
                self.key_list.pop(-1)
                if len(self.key_list) > 0 and self.key_list[-1].key == "Shift":
                    self.key_list.pop(-1)
            return

        if not self.key_list:
            self.start_time = datetime.now()

        key_object = KeyPressing()
        key_object.key = self.key_id_to_key(key_id)
        key_object.start_time = datetime.now() - self.start_time
        self.key_list.append(key_object)

    def release(self, key_id):
        if Qt.Key_Backspace == key_id:
            return
        if key_id == Qt.Key_Shift and self.key_list[-1].key == "Shift":
            self.key_list.pop(-1)
            return

        key = self.key_id_to_key(key_id)
        for key_object in self.key_list[::-1]:
            if key_object.key == key:
                key_object.end_time = datetime.now() - self.start_time
                break

    def serialize(self):
        res = list()
        for key in self.key_list:
            res.append(key.serialize())
        return res

    @property
    def intersections_1212(self):
        if len(self.key_list) < 2:
            return 0

        count = 0
        for key2 in self.key_list[1:]:
            for key1 in self.key_list:
                if key1 == key2:
                    break
                if key2.start_time < key1.end_time < key2.end_time:
                    count += 1

        return count

    @property
    def intersections_1221(self):
        if len(self.key_list) < 2:
            return 0

        count = 0
        for key2 in self.key_list[1:]:
            for key1 in self.key_list:
                if key1 == key2:
                    break
                if key2.start_time < key2.end_time < key1.end_time:
                    count += 1

        return count

    @property
    def average_pressing_time(self):
        if not self.key_list:
            return 0

        sum_time = timedelta()
        for key in self.key_list:
            sum_time += key.end_time - key.start_time
        return sum_time / len(self.key_list)

    @property
    def time_vector(self):
        keys = self.serialize()
        vector = [
            keys[0]["end"] - keys[0]["start"]
        ]
        last_end = keys[0]["end"]
        for key in keys[1:]:
            vector.append(key["start"] - last_end)
            last_end = key["end"]
            vector.append(key["end"] - key["start"])
        return vector


def register_password(): #регистрация пароля
    np_vectors = numpy.array(vectors)
    average_vector = numpy.mean(np_vectors, axis=0)

    i = 0
    dispersions = list()
    for column in np_vectors.T:
        dispersions.append((numpy.sum((column - average_vector[i])**2) / len(column))**0.5)
        i += 1
    dispersions = numpy.array(dispersions)

    min_vector = (average_vector - dispersions * 1.33).tolist() # минимальная граница
    max_vector = (average_vector + dispersions * 1.33).tolist() # максимальная граница

    queries.new_user(password, min_vector, max_vector)


def check_password(password, vector):
    user = queries.get_user(password)
    if user is None:
        return None

    error = len(vector)
    for i in range(error):
        error -= int(user.vector_min[i] <= vector[i] <= user.vector_max[i])

    return error, len(vector), error <= len(vector) * password_check_sensitivity
