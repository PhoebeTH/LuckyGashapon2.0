import random
import abc


# COLORS


GREEN  = "\033[92m"
PURPLE = "\033[95m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
RESET  = "\033[0m"



#ITEM CLASSES


class Item:
    """Base class for all gacha items."""

    def __init__(self, name: str, rarity: str, emoji: str):
        self.name   = name
        self.rarity = rarity
        self.emoji  = emoji

    def get_value(self) -> int:
        raise NotImplementedError("Subclasses must implement get_value()")

    def get_color(self) -> str:
        raise NotImplementedError("Subclasses must implement get_color()")

    def __str__(self) -> str:
        color = self.get_color()
        return f"{color}{self.emoji} {self.name} [{self.rarity}] — {self.get_value()} pts{RESET}"

    def to_dict(self) -> dict:
        return {"name": self.name, "rarity": self.rarity, "emoji": self.emoji}


class CommonItem(Item):
    """Common-tier item: low value, green display."""

    def __init__(self, name: str, emoji: str):
        super().__init__(name, "Common", emoji)

    def get_value(self) -> int:
        return 5

    def get_color(self) -> str:
        return GREEN


class RareItem(Item):
    """Rare-tier item: medium value, purple display."""

    def __init__(self, name: str, emoji: str):
        super().__init__(name, "Rare", emoji)

    def get_value(self) -> int:
        return 20

    def get_color(self) -> str:
        return PURPLE


class UltraRareItem(Item):
    """Ultra Rare-tier item: high value, gold display."""

    def __init__(self, name: str, emoji: str):
        super().__init__(name, "Ultra Rare", emoji)

    def get_value(self) -> int:
        return 50

    def get_color(self) -> str:
        return YELLOW


def item_from_dict(d: dict) -> Item:
    """Reconstruct an Item subclass from a saved dictionary."""
    name, rarity, emoji = d["name"], d["rarity"], d["emoji"]
    if rarity == "Common":
        return CommonItem(name, emoji)
    elif rarity == "Rare":
        return RareItem(name, emoji)
    else:
        return UltraRareItem(name, emoji)


# Item pools
COMMON_POOL: list[Item] = [
    # Consumables
    CommonItem("Health Potion",    "🧪"),
    CommonItem("Mana Potion",      "💧"),
    CommonItem("Antidote",         "🫧"),
    CommonItem("Smoke Bomb",       "💨"),
    CommonItem("Elixir",           "🍶"),
    # Currency / Junk
    CommonItem("Coins",            "🪙"),
    CommonItem("Old Map",          "🗺️"),
    CommonItem("Cracked Gem",      "🔮"),
    CommonItem("Rusty Key",        "🗝️"),
    CommonItem("Torn Scroll",      "📜"),
    # Creatures
    CommonItem("Slime",            "🟢"),
    CommonItem("Baby Bat",         "🦇"),
    CommonItem("Forest Sprite",    "🧚"),
    CommonItem("Sand Crab",        "🦀"),
    CommonItem("Glowworm",         "🐛"),
    # Weapons
    CommonItem("Wooden Sword",     "🗡️"),
    CommonItem("Hunting Bow",      "🏹"),
    CommonItem("Iron Dagger",      "🔪"),
    CommonItem("Wooden Shield",    "🛡️"),
    CommonItem("Stone Axe",        "🪓"),
    # Gear
    CommonItem("Leather Boots",    "👢"),
    CommonItem("Cloth Robe",       "👘"),
    CommonItem("Feather Cap",      "🪶"),
    CommonItem("Rope Belt",        "🧶"),
    CommonItem("Wool Cloak",       "🧣"),
    # Misc
    CommonItem("Candle",           "🕯️"),
    CommonItem("Fishing Rod",      "🎣"),
    CommonItem("Mushroom",         "🍄"),
    CommonItem("Lucky Coin",       "🪄"),
    CommonItem("Wooden Charm",     "🪵"),
]

RARE_POOL: list[Item] = [
    # Warriors
    RareItem("Silver Knight",      "⚔️"),
    RareItem("Battle Axe",         "🪓"),
    RareItem("War Hammer",         "🔨"),
    RareItem("Crossbow",           "🏹"),
    RareItem("Knight's Shield",    "🛡️"),
    # Mages
    RareItem("Magic Staff",        "🔮"),
    RareItem("Spell Tome",         "📖"),
    RareItem("Mana Crystal",       "💠"),
    RareItem("Enchanted Wand",     "🪄"),
    RareItem("Arcane Ring",        "💍"),
    # Fire
    RareItem("Fire Blade",         "🔥"),
    RareItem("Flame Bow",          "🏹"),
    RareItem("Ember Core",         "🔴"),
    RareItem("Volcanic Shard",     "🌋"),
    RareItem("Blazing Cloak",      "🧥"),
    # Ice / Nature
    RareItem("Frost Lance",        "🧊"),
    RareItem("Vine Whip",          "🌿"),
    RareItem("Storm Arrow",        "⚡"),
    RareItem("Moon Pendant",       "🌙"),
    RareItem("Thunder Gauntlet",   "🥊"),
]

ULTRA_POOL: list[Item] = [
    UltraRareItem("Golden Dragon",     "🐉"),
    UltraRareItem("Shadow Phoenix",    "🦅"),
    UltraRareItem("Crystal Titan",     "💎"),
    UltraRareItem("Void Reaper",       "💀"),
    UltraRareItem("Celestial Sword",   "🌟"),
    UltraRareItem("Abyssal Serpent",   "🐍"),
    UltraRareItem("Storm Emperor",     "⚡"),
    UltraRareItem("Sacred Unicorn",    "🦄"),
    UltraRareItem("Infernal Golem",    "🪨"),
    UltraRareItem("Divine Seraph",     "👼"),
]


def get_random_item(rarity: str) -> Item:
    """Return a random Item object for the given rarity string."""
    if rarity == "Common":
        return random.choice(COMMON_POOL)
    elif rarity == "Rare":
        return random.choice(RARE_POOL)
    else:
        return random.choice(ULTRA_POOL)



# PLAYER CLASS


class Player:
    """Holds all player state: points, inventory, pity, and spin history."""

    def __init__(self, points: int = 100):
        self.points:       int        = points
        self.inventory:    list[Item] = []
        self.pity_counter: int        = 0
        self.spin_count:   int        = 0
        self.spin_history: list[dict] = []  # Phase 4: each spin stored as a dict

    # ── Inventory helpers ──────────────────────

    def add_item(self, item: Item) -> None:
        self.inventory.append(item)

    def remove_item(self, item: Item) -> None:
        self.inventory.remove(item)

    def sorted_inventory(self) -> list[Item]:
        """Return inventory sorted by rarity then descending value (Phase 4)."""
        rarity_order = {"Ultra Rare": 0, "Rare": 1, "Common": 2}
        return sorted(
            self.inventory,
            key=lambda i: (rarity_order[i.rarity], -i.get_value())
        )

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

    def record_spin(self, rarity: str, item_name: str, guaranteed: bool) -> None:
        self.spin_history.append({
            "spin_num":   self.spin_count,
            "rarity":     rarity,
            "item_name":  item_name,
            "guaranteed": guaranteed,
        })

    def ultra_rare_count(self) -> int:
        return sum(1 for h in self.spin_history if h["rarity"] == "Ultra Rare")

    # ── Serialization (Phase 2) ────────────────

    def to_dict(self) -> dict:
        return {
            "points":       self.points,
            "pity_counter": self.pity_counter,
            "spin_count":   self.spin_count,
            "inventory":    [item.to_dict() for item in self.inventory],
            "spin_history": self.spin_history,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Player":
        p = cls(points=d["points"])
        p.pity_counter = d["pity_counter"]
        p.spin_count   = d["spin_count"]
        p.inventory    = [item_from_dict(i) for i in d["inventory"]]
        p.spin_history = d.get("spin_history", [])
        return p



# BANNER CLASSES


class Banner(abc.ABC):
    """Abstract base class for all gacha banners."""

    def __init__(self, name: str, description: str):
        self.name        = name
        self.description = description

    @abc.abstractmethod
    def spin(self, pity_counter: int) -> tuple[str, bool]:
        """
        Perform one spin and return (rarity_string, guaranteed_flag).
        Subclasses define their own rates and pity rules.
        """

    def __str__(self) -> str:
        return f"{CYAN}{self.name}{RESET} — {self.description}"


class StandardBanner(Banner):
    """
    Original drop rates with a 75-spin Ultra Rare pity guarantee.
    0.5% UR | 14.5% Rare | 85% Common
    """

    def __init__(self):
        super().__init__(
            "Standard Banner",
            (f"{YELLOW}0.5%{RESET} Ultra Rare  |  "
             f"{PURPLE}14.5%{RESET} Rare  |  "
             f"{GREEN}85%{RESET} Common  |  "
             f"{RED}UR guaranteed at 75 spins{RESET}")
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


class WeaponBanner(Banner):
    """
    Weapon-focused banner: higher Rare rate, no UR pity guarantee.
    0.7% UR | 29.3% Rare | 70% Common
    """

    def __init__(self):
        super().__init__(
            "Weapon Banner",
            (f"{YELLOW}0.7%{RESET} Ultra Rare  |  "
             f"{PURPLE}29.3%{RESET} Rare  |  "
             f"{GREEN}70%{RESET} Common  |  "
             f"{RED}No UR guarantee{RESET}")
        )

    def spin(self, pity_counter: int) -> tuple[str, bool]:
        roll = random.random()
        if roll < 0.007:
            return "Ultra Rare", False
        elif roll < 0.30:
            return "Rare", False
        else:
            return "Common", False


# All available banners
BANNERS: list[Banner] = [StandardBanner(), WeaponBanner()]
