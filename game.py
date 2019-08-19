import random

class Upgrade:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost
        
        self.owned = False
        
    def buy(self):
        self.owned = True
        
class ProducerMultiplierUpgrade(Upgrade):
    def __init__(self, name, cost, producer, multiplier):
        super().__init__(name, cost)
        self.producer = producer
        self.multiplier = multiplier
        
    def buy(self):
        super().buy()
        self.producer.multiplier *= self.multiplier
        
        
class ProducerAdditiveUpgrade(Upgrade):
    def __init__(self, name, cost, producer, add_amount):
        super().__init__(name, cost)
        self.producer = producer
        self.add_amount = add_amount
        
    def buy(self):
        super().buy()
        self.producer.add_pre += self.add_amount
        
class GameMultiplierUpgrade(Upgrade):
    def __init__(self, name, cost, game, multiplier):
        super().__init__(name, cost)
        self.game = game
        self.multiplier = multiplier
        
    def buy(self):
        super().buy()
        self.game.multiplier *= self.multiplier
        
        


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
        dict(type=GameMultiplierUpgrade, name="plain_cookies", cost=1e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="sugar_cookies", cost=5e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="oatmeal_raisin_cookies", cost=10e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="peanut_butter_cookies", cost=50e6, multiplier=1.01),
        dict(type=GameMultiplierUpgrade, name="coconut_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="almond_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="hazelnut_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="walnut_cookies", cost=100e6, multiplier=1.02),
        dict(type=GameMultiplierUpgrade, name="white_chocolate_cookies", cost=500e6, multiplier=1.02),
    
        # Cursor
        dict(type=ProducerMultiplierUpgrade, name="reinforced_index_finger", cost=100, producer="cursor", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="carpal_tunnel_prevention_cream", cost=500, producer="cursor", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="ambidextrous", cost=10000, producer="cursor", multiplier=2),
        
        # Grandma
        dict(type=ProducerMultiplierUpgrade, name="forwards_from_grandma", cost=1000, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="steel_plated_rolling_pins", cost=5000, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="lubricated_dentures", cost=50000, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="prune_juice", cost=5e6, producer="grandma", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="double_thick_glasses", cost=500e6, producer="grandma", multiplier=2),
        
        # Farm
        dict(type=ProducerMultiplierUpgrade, name="cheap_hoes", cost=11e3, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="fertilizer", cost=55e3, producer="farm", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="cookie_trees", cost=550e3, producer="farm", multiplier=2),
        
        # Mine
        dict(type=ProducerMultiplierUpgrade, name="sugar_gas", cost=120e3, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="megadrill", cost=600e3, producer="mine", multiplier=2),
        dict(type=ProducerMultiplierUpgrade, name="ultradrill", cost=6e6, producer="mine", multiplier=2),
    ]

    def __init__(self):
        self.total_cookies = 0
        self.cookies = 0
        self.turn = 0
        self.cpt = 0
        self.multiplier = 1
        
        self.producers = self._setup_producers()
        self.upgrades = self._setup_upgrades()
        
    def _setup_producers(self):
        return [Producer(*spec) for spec in self.producer_spec]
        
    def _setup_upgrades(self):
        upgrades = []
        for spec in self.upgrade_spec:
            if "producer" in spec and type(spec["producer"]) == str:
                spec["producer"] = self.get_producer(spec["producer"])
                
            if spec["type"] in (GameMultiplierUpgrade,):
                spec["game"] = self
            
            upgrades.append(spec["type"](**{k:v for k,v in spec.items() if k != "type"}))
            
        return upgrades
    
    def get_cpt(self):
        return sum(p.production for p in self.producers) * self.multiplier
        
    def get_producer(self, name):
        return next(p for p in self.producers if p.name == name)
    
    def advance(self):
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
            
            
    def click(self):
        self.cookies += 1
        
    def __str__(self):
        return "\n".join([
            f"Turn: {self.turn}, Cookies: {self.cookies:.1f}, Producing: {self.cpt:.1f}, Total: {self.total_cookies:.1f}",
            "Producers:",
            "\n".join(f"{p.name} - Owned: {p.n_owned}, Cost: {p.current_price:.0f}, Producing: {p.production:.1f}" for p in self.producers),
            "Upgrades:",
            "\n".join(f"{u.name} - Type: {u.__class__.__name__}" for u in self.upgrades if u.owned),
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
        self.production = 0
        self.multiplier = 1
        self.add_pre = 0
        self.add_post = 0
    
    def get_production(self):
        return (self.cpt + self.add_pre) * self.n_owned * self.multiplier + self.add_post
    
    def get_price(self, n):
        return int(self.base_price * self.price_scaling ** n)
    
    def buy(self):
        self.n_owned += 1
        self.current_price = self.get_price(self.n_owned)
        self.production = self.get_production()
        
    def sell(self):
        self.n_owned -= 1
        self.current_price = self.get_price(self.n_owned)
        self.production = self.get_production()
 
        
    
        
        
        
        