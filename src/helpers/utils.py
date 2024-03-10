from numpy.random import Generator, PCG64

class Utilities:
    def __init__(self):
        ...

    def _get_rng(self, seed: int):
        return Generator(PCG64(seed=seed))