from typing import List

from building import Building
from upgrade import Upgrade


class Game:
    """High level controller for the game."""

    upgrades: List[Upgrade]
    buildings: List[Building]
    cookies: float

    def __init__(self):
        self.upgrades = []
        self.cookies = 100

        self.__init_buildings()

    def __init_buildings(self) -> None:
        """Initialise buildings at the start of the game."""

        self.buildings = [
            cursor := Building("Cursor", 0.1, 10, 1.05),
            Building("Granny", 1, 50, 1.05),
            Building("Factory", 10, 200, 1.05),
        ]

        cursor.number_owned = 1

    @property
    def cookies_per_second(self) -> float:
        """Total number of cookies being produced per second, after upgrades."""

        return sum(b.cookies_per_second for b in self.buildings)

    def advance_game(self, time: float) -> None:
        """Advance the game by a given amount of time."""

        self.cookies += self.cookies_per_second * time

    def _get_building(self, building_name: str) -> Building:
        """Returns a building by name."""

        try:
            return next(b for b in self.buildings if b.name == building_name)
        except StopIteration:
            raise ValueError(f"Building not found: {building_name}")

    def buy_building(self, building_name: str) -> None:
        """Attempt to purchase a building."""

        building = self._get_building(building_name)

        if (cost := building.cost) <= self.cookies:
            self.cookies -= cost
            building.number_owned += 1
            print(f"Building purchased: {building.name} for {cost} cookies.")

        else:
            print(f"Unable to purchase building: {building.name}, insufficient cookies.")

    def __repr__(self):
        return f"Cookies: {self.cookies}, Per second: {self.cookies_per_second} Upgrades: {self.upgrades}, Buildings: {self.buildings}"


if __name__ == '__main__':
    game = Game()
    print(game)

    game.advance_game(5.3)
    print(game)

    game.buy_building("Cursor")
    print(game)

    game.buy_building("Factory")
    print(game)
