from building import Building


class Upgrade:
    """Defines how a building is upgraded."""

    name: str


class MultiplicativeUpgrade(Upgrade):
    """Multiplies the cookies per second by a scalar value."""

    value: float


class AdditiveUpgrade(Upgrade):
    """Adds a flat amount of cookies per second."""

    value: float
