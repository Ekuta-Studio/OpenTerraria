import random
import math

class PerlinNoise1D:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation += self.permutation  # Double the list for easy wrapping

    def fade(self, t):
        """Smooth interpolation function."""
        return t * t * t * (t * (t * 6 - 15) + 10)

    def lerp(self, a, b, t):
        """Linear interpolation between a and b."""
        return a + t * (b - a)

    def grad(self, hash, x):
        """Compute the gradient based on hash value."""
        h = hash & 15
        grad = 1 + (h & 7)  # Gradient value between 1 and 8
        if h & 8:
            grad = -grad  # Randomly flip the sign
        return grad * x

    def noise(self, x):
        """Generate Perlin noise at coordinate x."""
        # Find unit interval that contains x
        xi = int(x) & 255
        xf = x - int(x)

        # Fade curve for x
        u = self.fade(xf)

        # Hash coordinates of the interval corners
        a = self.permutation[xi]
        b = self.permutation[xi + 1]

        # Interpolate between the gradients
        return self.lerp(self.grad(a, xf), self.grad(b, xf - 1), u)