import math


class Building:
    """A building is an object which produces a number of cookies passively."""

    base_cookies_per_second: float
    number_owned: int
    name: str
    base_cost: float
    cost_scaling: float

    def __init__(self, name: str, cookies_per_second: float, base_cost: float, cost_scaling: float):
        self.name = name
        self.base_cookies_per_second = cookies_per_second
        self.base_cost = base_cost
        self.cost_scaling = cost_scaling

        self.number_owned = 0

    @property
    def cookies_per_second(self) -> float:
        """Cookies per second after all upgrades and modifiers are applied."""

        return self.base_cookies_per_second * self.number_owned

    @property
    def cost(self) -> int:
        """Cost of the building after all scaling and upgrades are applied."""

        return math.ceil(self.base_cost * self.cost_scaling ** self.number_owned)

    def __repr__(self):
        return f"{self.name}: {self.cookies_per_second} cps"
