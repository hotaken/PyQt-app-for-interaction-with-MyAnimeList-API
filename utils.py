from datetime import datetime, timedelta
from functools import wraps
import json
from functools import partial, wraps
import time
from cryptography.fernet import Fernet

# key = Fernet.generate_key()
# print(key)
key = b'F5qzsubis2ebhCTdJfQgMIVV3rl7ffQ_ovJnQXEu5as='


def save_encrypted(name, obj):
    str = json.dumps(obj)
    f = Fernet(key)
    encrypted_data = f.encrypt(str.encode())
    with open(name, "wb") as file:
        file.write(encrypted_data)
    return encrypted_data


def decrypt_from_file(path: str):
    f = Fernet(key)
    with open(path, "rb") as file:
        # read the encrypted data
        encrypted_data = file.read()
        decrypted_data = f.decrypt(encrypted_data)
        return json.loads(decrypted_data.decode())


def save_json(name, obj):
    with open(f'{name}.json', 'w') as file:
        json.dump(obj, file, indent=4)


def load_json(path):
    with open(path, 'r') as file:
        res = json.load(file)
    return res


class throttle(object):
    """
    Decorator that prevents a function from being called more than once every
    time period.
    To create a function that cannot be called more than once a minute:
        @throttle(minutes=1)
        def my_fun():
            pass
    """

    def __init__(self, seconds=0, minutes=0, hours=0):
        self.throttle_period = timedelta(
            seconds=seconds, minutes=minutes, hours=hours
        )
        self.time_of_last_call = datetime.min

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = datetime.now()
            time_since_last_call = now - self.time_of_last_call

            if time_since_last_call > self.throttle_period:
                self.time_of_last_call = now
                return fn(*args, **kwargs)
            print(f'Function {fn.__name__} call throttled')

        return wrapper
