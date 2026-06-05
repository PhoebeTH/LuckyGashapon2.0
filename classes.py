import random
import abc


# ── COLORS ────────────────────────────────────────────────────────────────────

GREEN  = "\033[92m"
PURPLE = "\033[95m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
RESET  = "\033[0m"


# ── SOUND EFFECTS ─────────────────────────────────────────────────────────────
import os as _os
import threading as _threading

_SFX_RARE     = "freesound_community-game-start-6104.wav"
_SFX_CHIME    = "49447089-game-start-317318.wav"
_SFX_GAMEOVER = "alphix-game-over-417465.wav"

def _sfx_base() -> str:
    return _os.path.dirname(_os.path.abspath(__file__))

def _init_audio() -> bool:
    return True

def _play(filename: str, wait: bool = False) -> None:

    try:
        import winsound
        path = _os.path.join(_sfx_base(), filename)
        if not _os.path.exists(path):
            return
        flags = winsound.SND_FILENAME
        if wait:
            winsound.PlaySound(path, flags)
        else:
            # Fire in a daemon thread so the game loop never blocks
            t = _threading.Thread(
                target=winsound.PlaySound,
                args=(path, flags),
                daemon=True,
            )
            t.start()
    except Exception:
        pass  # never crash the game over audio


# ── Public SFX API ────────────────────────────────────────────────────────────

def sfx_spin() -> None:
    pass

def sfx_rare() -> None:
    _play(_SFX_RARE)

def sfx_ultra() -> None:
    _play(_SFX_RARE)

def sfx_sell() -> None:
    _play(_SFX_CHIME)

def sfx_bonus() -> None:
    _play(_SFX_CHIME)

def sfx_gameover() -> None:
    _play(_SFX_GAMEOVER, wait=True)


# ── ITEM CLASSES ──────────────────────────────────────────────────────────────

class Item:
   

    def __init__(self, name: str, rarity: str, emoji: str, banner_tag: str = ""):
        self._name      = ""
        self._rarity    = rarity
        self.emoji      = emoji
        self.banner_tag = banner_tag   # e.g. "(B1)" or "(B2)"
        self.name       = name         # uses setter

   
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Item name must be a str, got {type(value).__name__}")
        self._name = value

    @property
    def rarity(self) -> str:
        return self._rarity

    def get_value(self) -> int:
        raise NotImplementedError("Subclasses must implement get_value()")

    def get_color(self) -> str:
        raise NotImplementedError("Subclasses must implement get_color()")

    def __str__(self) -> str:
        color  = self.get_color()
        tag    = f"{self.banner_tag} " if self.banner_tag else ""
        return f"{color}{tag}{self.emoji} {self.name} [{self.rarity}] — {self.get_value()} pts{RESET}"

    def to_dict(self) -> dict:
        return {
            "name":       self.name,
            "rarity":     self.rarity,
            "emoji":      self.emoji,
            "banner_tag": self.banner_tag,
        }


class CommonItem(Item):
    
    def __init__(self, name: str, emoji: str, banner_tag: str = ""):
        super().__init__(name, "Common", emoji, banner_tag)

    def get_value(self) -> int:
        return 3      # slightly reduced to balance NG+ economy

    def get_color(self) -> str:
        return GREEN


class RareItem(Item):
   

    def __init__(self, name: str, emoji: str, banner_tag: str = ""):
        super().__init__(name, "Rare", emoji, banner_tag)

    def get_value(self) -> int:
        return 20

    def get_color(self) -> str:
        return PURPLE


class UltraRareItem(Item):

    def __init__(self, name: str, emoji: str, banner_tag: str = ""):
        super().__init__(name, "Ultra Rare", emoji, banner_tag)

    def get_value(self) -> int:
        return 50

    def get_color(self) -> str:
        return YELLOW


# ── Professor fix: validated price/value helper (standalone) ─────────────────

def validate_price(value) -> float:
    
    if not isinstance(value, (int, float)):
        raise TypeError(f"Price must be int or float, got {type(value).__name__}")
    if value < 0:
        raise ValueError("Price cannot be negative.")
    return float(value)


def item_from_dict(d: dict) -> "Item":
   
    name       = d["name"]
    rarity     = d["rarity"]
    emoji      = d["emoji"]
    banner_tag = d.get("banner_tag", "")
    if rarity == "Common":
        return CommonItem(name, emoji, banner_tag)
    elif rarity == "Rare":
        return RareItem(name, emoji, banner_tag)
    else:
        return UltraRareItem(name, emoji, banner_tag)


# ── ITEM POOLS ────────────────────────────────────────────────────────────────
# Banner tag key:  (B1) 

COMMON_POOL: list[Item] = [
    # Consumables
    CommonItem("Health Potion",    "🧪",  "(B1)"),
    CommonItem("Mana Potion",      "💧",  "(B1)"),
    CommonItem("Antidote",         "🫧",  "(B1)"),
    CommonItem("Smoke Bomb",       "💨",  "(B1)"),
    CommonItem("Elixir",           "🍶",  "(B1)"),
    # Currency / Junk
    CommonItem("Coins",            "🪙",  "(B1)"),
    CommonItem("Old Map",          "🗺️",  "(B1)"),
    CommonItem("Cracked Gem",      "🔮",  "(B1)"),
    CommonItem("Rusty Key",        "🗝️",  "(B1)"),
    CommonItem("Torn Scroll",      "📜",  "(B1)"),
    # Creatures
    CommonItem("Slime",            "🟢",  "(B1)"),
    CommonItem("Baby Bat",         "🦇",  "(B1)"),
    CommonItem("Forest Sprite",    "🧚",  "(B1)"),
    CommonItem("Sand Crab",        "🦀",  "(B1)"),
    CommonItem("Glowworm",         "🐛",  "(B1)"),
    # Weapons
    CommonItem("Wooden Sword",     "🗡️",  "(B1)"),
    CommonItem("Hunting Bow",      "🏹",  "(B1)"),
    CommonItem("Iron Dagger",      "🔪",  "(B1)"),
    CommonItem("Wooden Shield",    "🛡️",  "(B1)"),
    CommonItem("Stone Axe",        "🪓",  "(B1)"),
    # Gear
    CommonItem("Leather Boots",    "👢",  "(B1)"),
    CommonItem("Cloth Robe",       "👘",  "(B1)"),
    CommonItem("Feather Cap",      "🪶",  "(B1)"),
    CommonItem("Rope Belt",        "🧶",  "(B1)"),
    CommonItem("Wool Cloak",       "🧣",  "(B1)"),
    # Misc
    CommonItem("Candle",           "🕯️",  "(B1)"),
    CommonItem("Fishing Rod",      "🎣",  "(B1)"),
    CommonItem("Mushroom",         "🍄",  "(B1)"),
    CommonItem("Lucky Coin",       "🪄",  "(B1)"),
    CommonItem("Wooden Charm",     "🪵",  "(B1)"),
]

RARE_POOL: list[Item] = [
    # Warriors
    RareItem("Silver Knight",      "⚔️",  "(B1)"),
    RareItem("Battle Axe",         "🪓",  "(B1)"),
    RareItem("War Hammer",         "🔨",  "(B1)"),
    RareItem("Crossbow",           "🏹",  "(B1)"),
    RareItem("Knight's Shield",    "🛡️",  "(B1)"),
    # Mages
    RareItem("Magic Staff",        "🔮",  "(B1)"),
    RareItem("Spell Tome",         "📖",  "(B1)"),
    RareItem("Mana Crystal",       "💠",  "(B1)"),
    RareItem("Enchanted Wand",     "🪄",  "(B1)"),
    RareItem("Arcane Ring",        "💍",  "(B1)"),
    # Fire
    RareItem("Fire Blade",         "🔥",  "(B1)"),
    RareItem("Flame Bow",          "🏹",  "(B1)"),
    RareItem("Ember Core",         "🔴",  "(B1)"),
    RareItem("Volcanic Shard",     "🌋",  "(B1)"),
    RareItem("Blazing Cloak",      "🧥",  "(B1)"),
    # Ice / Nature
    RareItem("Frost Lance",        "🧊",  "(B1)"),
    RareItem("Vine Whip",          "🌿",  "(B1)"),
    RareItem("Storm Arrow",        "⚡",  "(B1)"),
    RareItem("Moon Pendant",       "🌙",  "(B1)"),
    RareItem("Thunder Gauntlet",   "🥊",  "(B1)"),
]

ULTRA_POOL: list[Item] = [
    UltraRareItem("Golden Dragon",     "🐉",  "(B1)"),
    UltraRareItem("Shadow Phoenix",    "🦅",  "(B1)"),
    UltraRareItem("Crystal Titan",     "💎",  "(B1)"),
    UltraRareItem("Void Reaper",       "💀",  "(B1)"),
    UltraRareItem("Celestial Sword",   "🌟",  "(B1)"),
    UltraRareItem("Abyssal Serpent",   "🐍",  "(B1)"),
    UltraRareItem("Storm Emperor",     "⚡",  "(B1)"),
    UltraRareItem("Sacred Unicorn",    "🦄",  "(B1)"),
    UltraRareItem("Infernal Golem",    "🪨",  "(B1)"),
    UltraRareItem("Divine Seraph",     "👼",  "(B1)"),
]

# ── Bonus Banner (B2) ─────────────────────
BONUS_COMMON_POOL: list[Item] = [
    CommonItem("Pixie Dust",       "✨",  "(B2)"),
    CommonItem("Pebble",           "🪨",  "(B2)"),
    CommonItem("Butterfly",        "🦋",  "(B2)"),
    CommonItem("Acorn",            "🌰",  "(B2)"),
    CommonItem("Daisy",            "🌼",  "(B2)"),
    CommonItem("Lantern",          "🏮",  "(B2)"),
    CommonItem("Feather",          "🪶",  "(B2)"),
    CommonItem("Parchment",        "📄",  "(B2)"),
    CommonItem("Shard",            "🔷",  "(B2)"),
    CommonItem("Herb Bundle",      "🌿",  "(B2)"),
]

BONUS_RARE_POOL: list[Item] = [
    RareItem("Spirit Orb",         "🔵",  "(B2)"),
    RareItem("Shadow Blade",       "🌑",  "(B2)"),
    RareItem("Wind Fan",           "💨",  "(B2)"),
    RareItem("Tide Trident",       "🔱",  "(B2)"),
    RareItem("Earth Golem Fist",   "🪨",  "(B2)"),
]

BONUS_ULTRA_POOL: list[Item] = [
    UltraRareItem("Nebula Drake",      "🌌",  "(B2)"),
    UltraRareItem("Phantom Empress",   "👻",  "(B2)"),
    UltraRareItem("Sunfire Colossus",  "☀️",  "(B2)"),
    UltraRareItem("Abyssal Kraken",    "🐙",  "(B2)"),
    UltraRareItem("Starborn Paladin",  "⭐",  "(B2)"),
]

ALL_ITEMS: set[str] = (
    {i.name for i in COMMON_POOL}
    | {i.name for i in RARE_POOL}
    | {i.name for i in ULTRA_POOL}
    | {i.name for i in BONUS_COMMON_POOL}
    | {i.name for i in BONUS_RARE_POOL}
    | {i.name for i in BONUS_ULTRA_POOL}
)
TOTAL_UNIQUE_ITEMS = len(ALL_ITEMS)


def get_random_item(rarity: str, bonus: bool = False) -> "Item":
    
    if bonus:
        pool_map = {
            "Common":     BONUS_COMMON_POOL,
            "Rare":       BONUS_RARE_POOL,
            "Ultra Rare": BONUS_ULTRA_POOL,
        }
    else:
        pool_map = {
            "Common":     COMMON_POOL,
            "Rare":       RARE_POOL,
            "Ultra Rare": ULTRA_POOL,
        }
    return random.choice(pool_map[rarity])


# ── PLAYER CLASS ──────────────────────────────────────────────────────────────

class Player:
    

    def __init__(self, points: int = 150):   # buffed starting points
        self.points:         int        = points
        self.inventory:      list[Item] = []
        self.pity_counter:   int        = 0
        self.spin_count:     int        = 0
        self.spin_history:   list[dict] = []
        # NG+ tracking
        self.ng_plus_active: bool       = False
        self.ng_plus_record: int | None = None   # spins to full collection
        self.ng_plus_start:  int        = 0      # spin count when NG+ began

    # ── Inventory helpers ──────────────────────

    def add_item(self, item: Item) -> None:
        self.inventory.append(item)

    def remove_item(self, item: Item) -> None:
        self.inventory.remove(item)

    def sorted_inventory(self) -> list[Item]:
        rarity_order = {"Ultra Rare": 0, "Rare": 1, "Common": 2}
        return sorted(
            self.inventory,
            key=lambda i: (rarity_order[i.rarity], -i.get_value())
        )

    def unique_items_owned(self) -> set[str]:
        return {item.name for item in self.inventory}

    def unique_items_ever_pulled(self) -> set[str]:
        return {h["item_name"] for h in self.spin_history}

    # ── Economy helpers ────────────────────────

    def earn_points(self, amount: int) -> None:
        self.points += amount

    def spend_points(self, amount: int) -> bool:
        if self.points >= amount:
            self.points -= amount
            return True
        return False

    def is_broke(self) -> bool:
        return self.points < 10 and len(self.inventory) == 0

    # ── Spin tracking ──────────────────────────

    def record_spin(self, rarity: str, item_name: str, guaranteed: bool,
                    banner_name: str = "") -> None:
        self.spin_history.append({
            "spin_num":    self.spin_count,
            "rarity":      rarity,
            "item_name":   item_name,
            "guaranteed":  guaranteed,
            "banner_name": banner_name,
        })

    def ultra_rare_count(self) -> int:
        return sum(1 for h in self.spin_history if h["rarity"] == "Ultra Rare")

    # ── NG+ helpers ────────────────────────────

    def collection_complete(self) -> bool:
       
        return self.unique_items_ever_pulled() >= ALL_ITEMS

    def ng_plus_spins_used(self) -> int:
        return self.spin_count - self.ng_plus_start

    # ── Serialization ──────────────────────────

    def to_dict(self) -> dict:
        return {
            "points":         self.points,
            "pity_counter":   self.pity_counter,
            "spin_count":     self.spin_count,
            "inventory":      [item.to_dict() for item in self.inventory],
            "spin_history":   self.spin_history,
            "ng_plus_active": self.ng_plus_active,
            "ng_plus_record": self.ng_plus_record,
            "ng_plus_start":  self.ng_plus_start,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Player":
        p = cls(points=d["points"])
        p.pity_counter   = d["pity_counter"]
        p.spin_count     = d["spin_count"]
        p.inventory      = [item_from_dict(i) for i in d["inventory"]]
        p.spin_history   = d.get("spin_history", [])
        p.ng_plus_active = d.get("ng_plus_active", False)
        p.ng_plus_record = d.get("ng_plus_record", None)
        p.ng_plus_start  = d.get("ng_plus_start", 0)
        return p


# ── BANNER CLASSES ────────────────────────────────────────────────────────────

class Banner(abc.ABC):
 

    def __init__(self, name: str, description: str):
        self.name        = name
        self.description = description

    @abc.abstractmethod
    def spin(self, pity_counter: int) -> tuple[str, bool]:
        

    def __str__(self) -> str:
        return f"{CYAN}{self.name}{RESET} — {self.description}"


class StandardBanner(Banner):
   
    def __init__(self):
        super().__init__(
            "Standard Banner",
            (f"{YELLOW}0.5%{RESET} Ultra Rare  |  "
             f"{PURPLE}14.5%{RESET} Rare  |  "
             f"{GREEN}85%{RESET} Common  |  "
             f"{RED}UR guaranteed at 75 spins{RESET}  |  "
             f"💰 10 pts/spin  |  sells at FULL value")
        )

    def spin(self, pity_counter: int) -> tuple[str, bool]:
        if pity_counter >= 74:
            return "Ultra Rare", True
        roll = random.random()
        if roll < 0.005:
            return "Ultra Rare", False
        elif roll < 0.15:
            return "Rare", False
        else:
            return "Common", False


class BonusBanner(Banner):
   
    def __init__(self):
        super().__init__(
            "Bonus Banner  (FREE ROLLS)",
            (f"{YELLOW}1%{RESET} Ultra Rare  |  "
             f"{PURPLE}35%{RESET} Rare  |  "
             f"{GREEN}64%{RESET} Common  |  "
             f"{RED}No UR guarantee{RESET}  |  "
             f"✅ FREE to spin  |  sells at {YELLOW}60%{RESET} value")
        )

    def spin(self, pity_counter: int) -> tuple[str, bool]:
        roll = random.random()
        if roll < 0.01:
            return "Ultra Rare", False
        elif roll < 0.36:
            return "Rare", False
        else:
            return "Common", False

    @staticmethod
    def sell_multiplier() -> float:
        return 0.60


BANNERS: list[Banner] = [StandardBanner(), BonusBanner()]
