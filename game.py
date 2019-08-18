class CookieClickerGame:
    producer_spec = [
        ("cursor",              0.1,    15,     1.15),
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

    def __init__(self):
        self.cookies = 0
        self.turn = 0
        self.cpt = 0
        
        self.producers = self._setup_producers()
        
    def _setup_producers(self):
        return [Producer(*spec) for spec in self.producer_spec]
    
    def get_cpt(self):
        return sum(p.production for p in self.producers)
    
    def advance(self):
        self.cpt = self.get_cpt()
        self.cookies += self.cpt
        self.turn += 1
        
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
            print("Cant sell:", prod.name, ". Owned:", prod.n_owned)
            return False
            
            
    def click(self):
        self.cookies += 1
        
    def __str__(self):
        return "\n".join([
            f"Turn: {self.turn}, Cookies: {self.cookies:.1f}, Producing: {self.cpt:.1f}",
            "\n".join(f"{p.name} - Owned: {p.n_owned}, Cost: {p.current_price:.0f}, Producing: {p.production:.1f}" for p in self.producers)
        ])
        
    
class Producer:
    def __init__(self, name, cpt, base_price, price_scaling):
        self.name = name
        self.cpt = cpt # cookies per turn
        self.base_price = base_price
        self.price_scaling = price_scaling
        
        self.n_owned = 0
        self.current_price = base_price
        self.production = 0
    
    def get_price(self, n):
        return int(self.base_price * self.price_scaling ** n)
    
    def buy(self):
        self.n_owned += 1
        self.current_price = self.get_price(self.n_owned)
        self.production = self.cpt * self.n_owned
        
    def sell(self):
        self.n_owned -= 1
        self.current_price = self.get_price(self.n_owned)
        self.production = self.cpt * self.n_owned
        