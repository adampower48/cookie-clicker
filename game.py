import random
from abc import abstractmethod, ABCMeta
import operator as op
from functools import reduce

def prod(values):
    return reduce(op.mul, values, 1)

def format_large_num(x):
    """
    1234567 -> 1.23e6
    1 -> 1
    1.12345 -> 1.12
    1.6001 -> 1.6
    2.5012345 -> 2.5
    
    """

    if x > 1e6:
        return f"{x:.2e}"
        
    r = abs(round(x) - x)
    
    
    if r < 0.01: # eg 1.00001
        return str(int(round(x)))
    
    elif r % 0.1 < 0.01: # eg 3.60001
        return f"{round(x, 1):.1f}"
        
    
    return f"{round(x, 2):.2f}"


class Upgrade:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        
        self.owned = False
        
    def buy(self):
        self.owned = True
        
    def __str__(self):
        parts = [
            f"{self.name:<40s}",
            f"{self.__class__.__name__:<35s}",
        ]
    
        return "".join(parts)
            
class UpdateUpgrade(Upgrade, metaclass=ABCMeta):
    @abstractmethod
    def update(self):
        pass
        
class ProducerMultiplierUpgrade(Upgrade):
    def __init__(self, name, cost, producer, multiplier):
        super().__init__(name, cost)
        self.producer = producer
        self.multiplier = multiplier
        
    def buy(self):
        super().buy()
        self.producer.add_multi_func(self.get_multiplier)
        
    def get_multiplier(self):
        return self.multiplier
    
    def __str__(self):
        parts = [
            super().__str__(),
            f"{self.get_multiplier():<10d}",
        ]
        
        return "".join(parts)
        
class ProducerManyMultiplierUpgrade(Upgrade):
    def __init__(self, name, cost, producers, multiplier):
        super().__init__(name, cost)
        self.producers = producers
        self.multiplier = multiplier
    
    def buy(self):
        super().buy()
        for p in self.producers:
            p.add_multi_func(self.get_multiplier)
        
    def get_multiplier(self):
        return self.multiplier
    
    def __str__(self):
        parts = [
            super().__str__(),
            f"{self.get_multiplier():<10d}",
        ]
        
        return "".join(parts)

class ClickerCursorMultiplierUpgrade(Upgrade):
    def __init__(self, name, cost, cursor_producer, game, multiplier):
        super().__init__(name, cost)
        self.cursor_producer = cursor_producer
        self.multiplier = multiplier
        self.game = game
        
    def buy(self):
        super().buy()
        self.cursor_producer.add_multi_func(self.get_multiplier)
        self.game.clicker_multiplier_funcs.append(self.get_multiplier)
        
    def get_multiplier(self):
        return self.multiplier
    
    def __str__(self):
        parts = [
            super().__str__(),
            f"{self.get_multiplier():<10d}",
        ]
        
        return "".join(parts)

class ProducerAdditiveUpgrade(Upgrade):
    def __init__(self, name, cost, producer, add_amount):
        super().__init__(name, cost)
        self.producer = producer
        self.add_amount = add_amount
        
    def buy(self):
        super().buy()
        self.producer.add_add_pre_func(self.get_add)
        
    def get_add(self):
        return self.add_amount
        
class GameMultiplierUpgrade(Upgrade):
    def __init__(self, name, cost, game, multiplier):
        super().__init__(name, cost)
        self.game = game
        self.multiplier = multiplier
        
    def buy(self):
        super().buy()
        self.game.multiplier_funcs.append(self.get_multiplier)
        
    def get_multiplier(self):
        return self.multiplier
        
    def __str__(self):
        parts = [
            super().__str__(),
            f"{self.get_multiplier():<10.2f}",
        ]
        
        return "".join(parts)
        
class CursorAddPerOtherUpgrade(Upgrade):
    def __init__(self, name, cost, producers, game, add_amount):
        super().__init__(name, cost)
        self.cursor_producer = next(p for p in producers if p.name == "cursor")
        self.other_producers = [p for p in producers if p.name != "cursor"]
        self.add_amount = add_amount
        self.game = game
        
        self.old_n_owned = 0
        
    def buy(self):
        super().buy()
        self.game.clicker_add_funcs.append(self.get_add)
        self.cursor_producer.add_add_pre_func(self.get_add)
        
    def get_add(self):
        new_n_owned = sum(p.n_owned for p in self.other_producers)
        return self.add_amount * new_n_owned
        
    def __str__(self):
        parts = [
            super().__str__(),
            f"+{self.get_add():.1f}"
        ]
        
        return "".join(parts)

class ClickerAddCPSUpgrade(Upgrade):
    def __init__(self, name, cost, game, add_amount):
        super().__init__(name, cost)
        self.game = game
        self.add_amount = add_amount
        
    def buy(self):
        super().buy()
        self.game.clicker_add_funcs.append(self.get_add)
        
    def get_add(self):
        return self.game.get_cpt() * self.add_amount
        
    def __str__(self):
        parts = [
            super().__str__(),
            f"+{self.get_add():.1f}"
        ]
        
        return "".join(parts)
        
        
class ProducerMultiPerNGrandmasUpgrade(Upgrade):
    def __init__(self, name, cost, producer, grandma_producer, grandma_multi, prod_add_multi, per_n):
        super().__init__(name, cost)
        self.add_producer = producer
        self.add_multi = prod_add_multi
        self.grandma_producer = grandma_producer
        self.grandma_multi = grandma_multi
        self.per_n = per_n
        
        self.old_n_owned = 0
    
    def buy(self):
        super().buy()
        self.grandma_producer.multiplier_funcs.append(self.get_multiplier_grandma)
        self.add_producer.multiplier_funcs.append(self.get_multiplier_producer)
        
    def get_multiplier_producer(self):
        return 1 + self.add_multi * self.grandma_producer.n_owned / self.per_n
        
    def get_multiplier_grandma(self):
        return self.grandma_multi
        
        
    def __str__(self):
        parts = [
            super().__str__(),
            ", ".join([
                f"{int(self.get_multiplier_grandma()):d}",
                f"{self.get_multiplier_producer():.2f}",
            ])
        ]
        
        return "".join(parts)


class CookieClickerGame:
    producer_spec = [
        # name, production, cost, price_scaling
        ("cursor",              0.1,    15,     1.15), # todo: scaling
        ("grandma",             1,      100,    1.15),
        ("farm",                8,      1100,   1.15),
        ("mine",                47,     12e3,   1.15),
        ("factory",             260,    130e3,  1.15),
        ("bank",                1400,   1.4e6,  1.15),
        ("temple",              7800,   20e6,   1.15),
        ("wizard_tower",        44e3,   330e6,  1.15),
        ("shipment",            260e3,  5.1e9,  1.15),
        ("alchemy_lab",         1.6e6,  75e9,   1.15),
        ("portal",              10e6,   1e12,   1.15),
        ("time_machine",        65e6,   14e12,  1.15),
        ("antimatter_condenser",430e6,  170e12, 1.15),
        ("prism",               2.9e9,  2.1e15, 1.15),
        ("chancemaker",         21e9,   26e15,  1.15),
        ("fractal_engine",      150e9,  310e15, 1.15),
    ]
    
    upgrade_spec = [
        # Game
        ## Multipliers
        dict(type=GameMultiplierUpgrade, name="plain_cookies", cost=1e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="sugar_cookies", cost=5e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="oatmeal_raisin_cookies", cost=10e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="peanut_butter_cookies", cost=50e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="coconut_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="almond_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="hazelnut_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="walnut_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="white_chocolate_cookies", cost=500e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="macadamia_nut_cookies", cost=1e9, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="double_chip_cookies", cost=5e9, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="white_chocolate_macadamia_nut_cookies", cost=10e9, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="all_chocolate_cookies", cost=50e9, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="dark_chocolate_coated_cookies", cost=100e9, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="white_chocolate_coated_cookies", cost=100e9, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="eclipse_cookies", cost=500e9, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="zebra_cookies", cost=1e12, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="snickerdoodles", cost=5e12, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="stroopwafeles", cost=10e12, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="macaroon", cost=50e12, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="empire_biscuit", cost=100e12, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="madeleines", cost=500e12, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="palmiers", cost=500e12, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="palets", cost=1e15, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="sables", cost=1e15, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="gingerbread_men", cost=10e15, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="gingerbread_trees", cost=10e15, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="pure_black_chocolate_cookies", cost=50e15, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="pure_white_chocolate_cookies", cost=50e15, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="ladyfingers", cost=100e15, multiplier=1.03),
        dict(type=GameMultiplierUpgrade, name="tuiles", cost=500e15, multiplier=1.03),
        dict(type=GameMultiplierUpgrade, name="chocolate_stuffed_cookies", cost=1e18, multiplier=1.03),
        dict(type=GameMultiplierUpgrade, name="checker_cookies", cost=5e18, multiplier=1.03),
        dict(type=GameMultiplierUpgrade, name="butter_cookies", cost=10e18, multiplier=1.03),
        dict(type=GameMultiplierUpgrade, name="cream_cookies", cost=50e18, multiplier=1.03),
        dict(type=GameMultiplierUpgrade, name="gingersnaps", cost=100e18, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="cinnamon_cookies", cost=500e18, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="vanity_cookies", cost=1e21, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="milk_chocolate_butter_biscuit", cost=1e21, multiplier=1.1),
        dict(type=GameMultiplierUpgrade, name="cigars", cost=5e21, multiplier=1.04),
        dict(type=GameMultiplierUpgrade, name="dark_chocolate_butter_biscuit", cost=1e24, multiplier=1.1),
        dict(type=GameMultiplierUpgrade, name="white_chocolate_butter_biscuit", cost=1e27, multiplier=1.1),
    
        ## Clicker
        dict(type=ClickerAddCPSUpgrade, name="plastic_mouse", cost=50e3, add_amount=0.01),
        dict(type=ClickerAddCPSUpgrade, name="iron_mouse", cost=5e6, add_amount=0.01),
        dict(type=ClickerAddCPSUpgrade, name="titanium_mouse", cost=500e6, add_amount=0.01),
        dict(type=ClickerAddCPSUpgrade, name="adamantium_mouse", cost=50e9, add_amount=0.01),
        dict(type=ClickerAddCPSUpgrade, name="unobtanium_mouse", cost=5e12, add_amount=0.01),
        dict(type=ClickerAddCPSUpgrade, name="eludium_mouse", cost=500e12, add_amount=0.01),
        
    
        # Cursor
        ## Multipliers
        dict(type=ClickerCursorMultiplierUpgrade, name="reinforced_index_finger", cost=100, cursor_producer="cursor", multiplier=2),
        dict(type=ClickerCursorMultiplierUpgrade, name="carpal_tunnel_prevention_cream", cost=500, cursor_producer="cursor", multiplier=2),
        dict(type=ClickerCursorMultiplierUpgrade, name="ambidextrous", cost=10000, cursor_producer="cursor", multiplier=2),
        
        ## Additive Per Other
        dict(type=CursorAddPerOtherUpgrade, name="thousand_fingers", cost=100e3, add_amount=0.1),
        dict(type=CursorAddPerOtherUpgrade, name="million_fingers", cost=10e6, add_amount=0.5),
        dict(type=CursorAddPerOtherUpgrade, name="billion_fingers", cost=100e6, add_amount=5),
        dict(type=CursorAddPerOtherUpgrade, name="trillion_fingers", cost=1e9, add_amount=50),
        dict(type=CursorAddPerOtherUpgrade, name="quadrillion_fingers", cost=10e9, add_amount=500),
        dict(type=CursorAddPerOtherUpgrade, name="quintillion_fingers", cost=10e12, add_amount=5000),
        dict(type=CursorAddPerOtherUpgrade, name="sextillion_fingers", cost=10e15, add_amount=50000),
        
        
        # Grandma
        ## Multipliers
        dict(type=ProducerMultiplierUpgrade, name="forwards_from_grandma", cost=1000, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="steel_plated_rolling_pins", cost=5000, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="lubricated_dentures", cost=50000, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="prune_juice", cost=5e6, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="double_thick_glasses", cost=500e6, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="aging_agents", cost=50e9, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="xtreme_walkers", cost=50e12, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="the_unbridling", cost=50e15, producer="grandma", multiplier=2),
        
        ## Multipliers + % per n grandmas
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="farmer_grandmas", cost=55e3, producer="farm", grandma_multi=2, prod_add_multi=0.01, per_n=1),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="miner_grandmas", cost=600e3, producer="mine", grandma_multi=2, prod_add_multi=0.01, per_n=2),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="worker_grandmas", cost=6.5e6, producer="factory", grandma_multi=2, prod_add_multi=0.01, per_n=3),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="banker_grandmas", cost=70e6, producer="bank", grandma_multi=2, prod_add_multi=0.01, per_n=4),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="priestess_grandmas", cost=1e9, producer="temple", grandma_multi=2, prod_add_multi=0.01, per_n=5),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="witch_grandmas", cost=16.5e9, producer="wizard_tower", grandma_multi=2, prod_add_multi=0.01, per_n=6),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="cosmic_grandmas", cost=255e9, producer="shipment", grandma_multi=2, prod_add_multi=0.01, per_n=7),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="transmuted_grandmas", cost=3.75e12, producer="alchemy_lab", grandma_multi=2, prod_add_multi=0.01, per_n=8),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="altered_grandmas", cost=50e12, producer="portal", grandma_multi=2, prod_add_multi=0.01, per_n=9),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="grandmas_grandmas", cost=700e15, producer="time_machine", grandma_multi=2, prod_add_multi=0.01, per_n=10),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="antigrandmas", cost=8.5e18, producer="antimatter_condenser", grandma_multi=2, prod_add_multi=0.01, per_n=11),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="rainbow_grandmas", cost=105e18, producer="prism", grandma_multi=2, prod_add_multi=0.01, per_n=12),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="lucky_grandmas", cost=1.3e21, producer="chancemaker", grandma_multi=2, prod_add_multi=0.01, per_n=13),
        dict(type=ProducerMultiPerNGrandmasUpgrade, name="metagrandmas", cost=15.5e21, producer="fractal_engine", grandma_multi=2, prod_add_multi=0.01, per_n=14),
        
        # Farm
        dict(type=ProducerMultiplierUpgrade, name="cheap_hoes", cost=11e3, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="fertilizer", cost=55e3, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="cookie_trees", cost=550e3, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="genetically_modified_cookies", cost=55e6, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="gingerbread_scarecrows", cost=5.5e9, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="pulsar_sprinklers", cost=550e9, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="fudge_fungus", cost=550e12, producer="farm", multiplier=2),
        
        # Mine
        dict(type=ProducerMultiplierUpgrade, name="sugar_gas", cost=120e3, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="megadrill", cost=600e3, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="ultradrill", cost=6e6, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="ultimadrill", cost=600e6, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="h_bomb_mining", cost=60e9, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="coreforge", cost=6e12, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="planetsplitters", cost=6e15, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="canola_oil_wells", cost=6e18, producer="mine", multiplier=2),
        
        # Factory
        dict(type=ProducerMultiplierUpgrade, name="sturdier_conveyor_belts", cost=1.3e6, producer="factory", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="child_labor", cost=6.5e6, producer="factory", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="sweatshop", cost=65e6, producer="factory", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="radium_reactors", cost=6.5e9, producer="factory", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="recombobulators", cost=650e9, producer="factory", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="deep_bake_process", cost=65e12, producer="factory", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="cyborg_workforce", cost=65e15, producer="factory", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="78_hour_days", cost=65e18, producer="factory", multiplier=2),
        
        # Bank
        dict(type=ProducerMultiplierUpgrade, name="taller_tellers", cost=14e6, producer="bank", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="scissor_resistant_credit_cards", cost=70e6, producer="bank", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="acid_prood_vaults", cost=700e6, producer="bank", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="chocolate_coins", cost=70e9, producer="bank", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="exponential_interest_rates", cost=7e12, producer="bank", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="financial_zen", cost=700e12, producer="bank", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="way_of_the_wallet", cost=700e15, producer="bank", multiplier=2),
        
        # Temple
        dict(type=ProducerMultiplierUpgrade, name="golden_idols", cost=200e6, producer="temple", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="sacrifices", cost=1e9, producer="temple", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="delicious_blessing", cost=10e9, producer="temple", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="sun_festival", cost=1e12, producer="temple", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="enlarged_pantheon", cost=100e12, producer="temple", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="great_baker_in_the_sky", cost=10e15, producer="temple", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="creation_myth", cost=10e18, producer="temple", multiplier=2),
        
        # Wizard Tower
        dict(type=ProducerMultiplierUpgrade, name="pointier_hats", cost=3.3e9, producer="wizard_tower", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="beardier_beards", cost=16.5e9, producer="wizard_tower", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="ancient_grimoires", cost=165e9, producer="wizard_tower", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="kitchen_curses", cost=16.5e12, producer="wizard_tower", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="school_of_sorcery", cost=1.65e15, producer="wizard_tower", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="dark_formulas", cost=165e15, producer="wizard_tower", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="cookiemancy", cost=165e18, producer="wizard_tower", multiplier=2),
        
        # Shipment
        dict(type=ProducerMultiplierUpgrade, name="vanilla_nebulae", cost=51e9, producer="shipment", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="wormholes", cost=255e9, producer="shipment", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="frequent_flyer", cost=2.55e12, producer="shipment", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="warp_drive", cost=255e12, producer="shipment", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="chocolate_monoliths", cost=25.5e15, producer="shipment", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="generation_ship", cost=2.55e18, producer="shipment", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="dyson_sphere", cost=2.55e21, producer="shipment", multiplier=2),
        
        # Alchemy Lab
        dict(type=ProducerMultiplierUpgrade, name="antimony", cost=750e9, producer="alchemy_lab", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="essence_of_dough", cost=3.75e12, producer="alchemy_lab", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="true_chocolate", cost=37.5e12, producer="alchemy_lab", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="ambrosia", cost=3.75e15, producer="alchemy_lab", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="aqua_crustulae", cost=375e15, producer="alchemy_lab", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="origin_crucible", cost=37.5e18, producer="alchemy_lab", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="theory_of_atomic_fluidity", cost=37.5e21, producer="alchemy_lab", multiplier=2),
        
        # Portal
        dict(type=ProducerMultiplierUpgrade, name="ancient_tablet", cost=10e12, producer="portal", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="insane_oatling_workers", cost=50e12, producer="portal", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="soul_bond", cost=500e12, producer="portal", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="sanity_dance", cost=50e15, producer="portal", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="brane_transplant", cost=5e18, producer="portal", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="deity_sized_portals", cost=500e18, producer="portal", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="end_of_times_backup_plan", cost=500e21, producer="portal", multiplier=2),
        
        # Time Machine
        dict(type=ProducerMultiplierUpgrade, name="flux_capacitors", cost=140e12, producer="time_machine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="time_paradox_resolver", cost=700e12, producer="time_machine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="quantum_conundrum", cost=7e15, producer="time_machine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="causality_enforcer", cost=700e15, producer="time_machine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="yestermorrow_comparators", cost=70e18, producer="time_machine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="far_future_enactment", cost=7e21, producer="time_machine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="great_loop_hypothesis", cost=7e24, producer="time_machine", multiplier=2),
        
        # Antimatter Condenser
        dict(type=ProducerMultiplierUpgrade, name="sugar_bosons", cost=1.7e15, producer="antimatter_condenser", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="string_theory", cost=8.5e15, producer="antimatter_condenser", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="large_macaron_collider", cost=85e15, producer="antimatter_condenser", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="big_bang_bake", cost=8.5e18, producer="antimatter_condenser", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="reverse_cyclotrons", cost=850e18, producer="antimatter_condenser", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="nanocosmics", cost=85e21, producer="antimatter_condenser", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="the_pulse", cost=85e24, producer="antimatter_condenser", multiplier=2),
        
        # Prism
        dict(type=ProducerMultiplierUpgrade, name="gem_polish", cost=21e15, producer="prism", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="9th_color", cost=105e15, producer="prism", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="chocolate_light", cost=1.05e18, producer="prism", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="grainbow", cost=105e18, producer="prism", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="pure_cosmic_light", cost=10.5e21, producer="prism", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="glow_in_the_dark", cost=1.05e24, producer="prism", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="lux_sanctorum", cost=1.05e27, producer="prism", multiplier=2),
        
        # Chancemaker
        dict(type=ProducerMultiplierUpgrade, name="your_lucky_cookie", cost=260e15, producer="chancemaker", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="all_bets_are_off_magic_coin", cost=1.3e18, producer="chancemaker", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="winning_lottery_ticket", cost=13e18, producer="chancemaker", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="four_leaf_clover_field", cost=1.3e21, producer="chancemaker", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="a_recipe_book_about_books", cost=130e21, producer="chancemaker", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="leprechaun_village", cost=13e24, producer="chancemaker", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="improbability_drive", cost=13e27, producer="chancemaker", multiplier=2),
        
        # Fractal Engine
        dict(type=ProducerMultiplierUpgrade, name="metabakeries", cost=3.1e18, producer="fractal_engine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="mandelbrown_sugar", cost=15.5e18, producer="fractal_engine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="fractoids", cost=155e18, producer="fractal_engine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="nested_universe_theory", cost=15.5e21, producer="fractal_engine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="mengar_sponge_cake", cost=1.55e24, producer="fractal_engine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="one_particularly_good_humored_cow", cost=155e24, producer="fractal_engine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="chocolate_ouroboros", cost=155e27, producer="fractal_engine", multiplier=2),
    ]

    def __init__(self):
        self.total_cookies = 0
        self.cookies = 0
        self.turn = 0
        self.cpt = 0
        self.multiplier_funcs = []
        self.clicker_add_funcs = []
        self.clicker_multiplier_funcs = []
        
        
        self.producers = self._setup_producers()
        self.upgrades = self._setup_upgrades()
        
    def _setup_producers(self):
        return [Producer(*spec) for spec in self.producer_spec]
        
    def _setup_upgrades(self):
        upgrades = []
        for spec in self.upgrade_spec:
            if "producer" in spec:
                spec["producer"] = self.get_producer(spec["producer"])
                
            if "cursor_producer" in spec:
                spec["cursor_producer"] = self.get_producer(spec["cursor_producer"])
                
            
            if spec["type"] in (CursorAddPerOtherUpgrade,):
                spec["producers"] = self.producers
                
            if spec["type"] in (GameMultiplierUpgrade, CursorAddPerOtherUpgrade, ClickerAddCPSUpgrade, ClickerCursorMultiplierUpgrade):
                spec["game"] = self
                
            if spec["type"] in (ProducerMultiPerNGrandmasUpgrade,):
                spec["grandma_producer"] = self.get_producer("grandma")
            
            upgrades.append(spec["type"](**{k:v for k,v in spec.items() if k != "type"}))
            
        return upgrades
    
    def _update_upgrades(self):
        for upgr in self.upgrades:
            if issubclass(upgr.__class__, UpdateUpgrade):
                upgr.update()
    
    
    def get_cpt(self):
        return sum(p.get_production() for p in self.producers) * self.get_multi()
        
    def get_producer(self, name):
        return next(p for p in self.producers if p.name == name)
        
    def get_multi(self):
        return prod(f() for f in self.multiplier_funcs)
    
    def advance(self):
        self._update_upgrades()
    
        self.cpt = self.get_cpt()
        self.cookies += self.cpt
        self.total_cookies += self.cpt
        self.turn += 1
        
    def buy_upgrade(self, idx):
        upgrade = self.upgrades[idx]
        cost = upgrade.cost
        
        if upgrade.owned:
            print(f"Upgrade: {upgrade.name} already owned.")
            return False
        
        if cost <= self.cookies:
            print(f"Bought: {upgrade.name} for {upgrade.cost}. Cookies: {self.cookies} -> ", end="")
            self.cookies -= cost
            upgrade.buy()
            print(f"{self.cookies:.1f}")
            
            return True
        else:
            print(f"Cant afford upgrade: {upgrade.name} for {upgrade.cost:.0f} with {self.cookies:.1f}")
            return False
        
    def buy_producer(self, idx):
        prod = self.producers[idx]
        cost = prod.current_price
        if cost <= self.cookies:
            print(f"Bought: {prod.name} for {prod.current_price}. Cookies: {self.cookies} -> ", end="")
            self.cookies -= cost
            prod.buy()
            print(f"{self.cookies:.1f}")
            
            return True
        else:
            print(f"Cant afford producer: {prod.name} for {prod.current_price:.0f} with {self.cookies:.1f}")
            return False
            
    def sell_producer(self, idx):
        prod = self.producers[idx]
        
        if prod.n_owned > 0:
            
            _cookies = self.cookies
            prod.sell()
            self.cookies += prod.current_price
            print("Sold:", prod.name, "for", prod.current_price, ". Cookies:", _cookies, "->", self.cookies)
            
            return True
        
        else:
            print(f"Cant sell: {prod.name}. Owned: {prod.n_owned}")
            return False
            
    def get_cpc(self):
        return (1 + sum(f() for f in self.clicker_add_funcs)) * prod(f() for f in self.clicker_multiplier_funcs)
    
    def click(self):
        self.cookies += self.get_cpc()
        
    def __str__(self):
        return "\n".join([
            f"Turn: {self.turn}, Cookies: {format_large_num(self.cookies)}, Producing: {format_large_num(self.cpt)}, Total: {format_large_num(self.total_cookies)}",
            f"Cookies/click: {format_large_num(self.get_cpc())}, ClickerMultis: {str([f() for f in self.clicker_multiplier_funcs])}",
            "Producers:",
            f"{'Name':<25s}{'Owned':<10s}{'Cost':<15s}{'Producing':<20s}{'Multis':<20s}",
            "\n".join(map(str, self.producers)),
            "Upgrades:",
            f"{'Name':<40s}{'Type':<35s}{'Multi':<10s}",
            "\n".join(str(u) for u in self.upgrades if u.owned),
        ])
        
    def get_available_actions(self):
        def _pass():
            pass
    
        actions = []
        
        actions.append([_pass])
        
        actions.append([self.click])
        
        avail_buy_prod = [[i] for i, p in enumerate(self.producers) if p.current_price <= self.cookies]
        actions.append([self.buy_producer, avail_buy_prod])
        
        avail_sell_prod = [[i] for i, p in enumerate(self.producers) if p.n_owned > 0]
        actions.append([self.sell_producer, avail_sell_prod])
        
        avail_buy_upgr = [[i] for i, u in enumerate(self.upgrades) if not u.owned and u.cost <= self.cookies]
        actions.append([self.buy_upgrade, avail_buy_upgr])
            
        return actions
    
    def random_action(self, weights=None):
        """
        weights: [pass, click, buy_prod, sell_prod, buy_upgr]
        
        """
    
        def update_weights(weights):
            if weights is None:
                weights = [1, 1, 1, 1, 1]
        
            for i, action in enumerate(avail_actions):
                if len(action) > 1 and len(action[1]) == 0:
                    weights[i] = 0
            
            return weights


            
    
        avail_actions = self.get_available_actions()
        weights = update_weights(weights)
        
        action = random.choices(avail_actions, weights, k=1)[0]
        if len(action) == 1:
            action[0]()
        else:
            args = random.choice(action[1])
            action[0](*args)
            
    
    
class Producer:
    def __init__(self, name, cpt, base_price, price_scaling):
        self.name = name
        self.cpt = cpt # cookies per turn
        self.base_price = base_price
        self.price_scaling = price_scaling
        
        self.n_owned = 0
        self.current_price = base_price
        self.multiplier_funcs = []
        self.add_pre_funcs = []
        self.add_post_funcs = []

    
    def get_production(self):
        return (self.cpt + self.get_add_pre()) * self.n_owned * self.get_multi() + self.get_add_post()
    
    def get_multi(self):
        return prod(self.get_multis())
    
    def get_multis(self):
        return [f() for f in self.multiplier_funcs]
        
    def get_add_pre(self):
        return sum(self.get_add_pres())
    
    def get_add_pres(self):
        return [f() for f in self.add_pre_funcs]
        
    def get_add_post(self):
        return sum(self.get_add_posts())
    
    def get_add_posts(self):
        return [f() for f in self.add_post_funcs]
        
    def add_multi_func(self, func):
        self.multiplier_funcs.append(func)
        
    def add_add_pre_func(self, func):
        self.add_pre_funcs.append(func)
    
    def add_add_post_func(self, func):
        self.add_post_funcs.append(func)
       
    
    def get_price(self, n):
        return int(self.base_price * self.price_scaling ** n)
    
    def buy(self):
        self.n_owned += 1
        self.current_price = self.get_price(self.n_owned)
        
    def sell(self):
        self.n_owned -= 1
        self.current_price = self.get_price(self.n_owned)
 
    def __str__(self):
        parts = [
            f"{self.name:<25s}",
            f"{int(self.n_owned):<10d}",
            f"{format_large_num(self.current_price):<15s}",
            f"{format_large_num(self.get_production()):<20s}",
            "{:<10s}".format(" ".join(
                format_large_num(m) for m in self.get_multis()
            )),
        ]
        
        return "".join(parts)
    