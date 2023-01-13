
import random
import contextlib


@contextlib.contextmanager
def seed_random(seed: str):
    prev_state = random.getstate()
    random.seed(seed)
    try:
        yield
    finally:
        random.setstate(prev_state)


def generate_token(length: int = 8):
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return "".join(random.choices(alphabet, k=length))
