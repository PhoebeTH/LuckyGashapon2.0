import random
import time
import os
import json

from classes import (
    GREEN, PURPLE, YELLOW, CYAN, RED, RESET,
    Item, Player, Banner, StandardBanner,
    item_from_dict, get_random_item, BANNERS,
)

SAVE_FILE        = "save.json"
LEADERBOARD_FILE = "leaderboard.json"



# FILE I/O

def save_player(player: Player) -> None:
    with open(SAVE_FILE, "w") as f:
        json.dump(player.to_dict(), f, indent=2)
    print(GREEN + "✅ Game saved!" + RESET)


def load_player() -> "Player | None":
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r") as f:
            return Player.from_dict(json.load(f))
    except Exception:
        return None


def delete_save() -> None:
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def load_leaderboard() -> list[dict]:
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def update_leaderboard(player: Player, banner_name: str) -> None:
    """Append this session and keep the top 5 by Ultra Rares pulled."""
    board = load_leaderboard()
    board.append({
        "ultra_rares": player.ultra_rare_count(),
        "spins":       player.spin_count,
        "points":      player.points,
        "banner":      banner_name,
    })
    board.sort(key=lambda x: x["ultra_rares"], reverse=True)
    board = board[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)


def show_leaderboard() -> None:
    board = load_leaderboard()
    print(YELLOW + "\n🏆 TOP 5 LEADERBOARD (by Ultra Rares pulled)" + RESET)
    print("-" * 50)
    if not board:
        print("  No sessions recorded yet.")
    else:
        for rank, entry in enumerate(board, 1):
            print(f"  {rank}. {YELLOW}{entry['ultra_rares']} URs{RESET}  |  "
                  f"{entry['spins']} spins  |  "
                  f"{entry['points']} pts  |  "
                  f"{CYAN}{entry['banner']}{RESET}")
    print("-" * 50)


#
# DISPLAY
#

def draw_logo() -> None:
    logo = [
        "██     ██  ██ ▄█████ ██ ▄█▀ ██  ██",
        "██     ██  ██ ██     ████    ▀██▀",
        "██████ ▀████▀ ▀█████ ██ ▀█▄   ██",
        "",
        " ▄████  ▄████▄ ▄█████ ██  ██ ▄████▄ █████▄ ▄████▄ ███  ██",
        "██  ▄▄▄ ██▄▄██ ██     ██████ ██▄▄██ ██▄▄█▀ ██  ██ ██ ▀▄██",
        " ▀███▀  ██  ██ ▀█████ ██  ██ ██  ██ ██     ▀████▀ ██   ██",
    ]
    colors = [RED, YELLOW, GREEN, CYAN, PURPLE]
    for i, line in enumerate(logo):
        print(colors[i % len(colors)] + line + RESET)


def display_intro() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    draw_logo()
    print()
    print(YELLOW + "Ultra Rare drop rate: 0.5% 🌟")
    print(PURPLE + "Rare drop rate: 14.5% 💎")
    print(GREEN  + "Common drop rate: 85% 🪙")
    print(RED    + "Ultra Rare GUARANTEED at 75 spins (Standard Banner only)!" + RESET)
    print("\nStart with 100 points. Each spin costs 10 points.")
    print("-" * 40)


def pity_bar(pity: int, max_pity: int = 75) -> None:
    total  = 20
    filled = int(pity * total / max_pity)
    bar    = "█" * filled + "░" * (total - filled)
    print(CYAN + f"Pity: [{bar}] {pity}/{max_pity}" + RESET)


def spin_animation() -> None:
    print("Spinning", end="")
    for _ in range(3):
        time.sleep(0.2)
        print(".", end="", flush=True)
    print()


def bonus_event(player: Player) -> None:
    if random.random() < 0.10:
        print(CYAN + "🎁 BONUS! +5 points!" + RESET)
        player.earn_points(5)


# STORE


def open_store(player: Player) -> None:
    while player.inventory:
        print(CYAN + "\n🛒 STORE — Sell Items" + RESET)
        sorted_inv = player.sorted_inventory()
        for i, item in enumerate(sorted_inv, 1):
            print(f"  {i}. {item}")

        print("\nType item numbers (example: 1 2 3)")
        print("a = sell everything  |  e = exit store")
        choice = input("Choice: ").lower().strip()

        if choice == "e":
            break

        elif choice == "a":
            total = sum(item.get_value() for item in player.inventory)
            player.inventory.clear()
            player.earn_points(total)
            print(CYAN + f"Sold EVERYTHING for {total} points! 💰" + RESET)

        else:
            parts = choice.split()
            if all(p.isdigit() for p in parts):
                indexes = sorted({int(p) - 1 for p in parts}, reverse=True)
                total_value = 0
                for idx in indexes:
                    if 0 <= idx < len(sorted_inv):
                        item = sorted_inv[idx]
                        if item in player.inventory:
                            player.remove_item(item)
                            total_value += item.get_value()
                            print(f"  Sold {item} 💰")
                player.earn_points(total_value)
                if total_value:
                    print(CYAN + f"Total gained: {total_value} points! 💰" + RESET)
            else:
                print(RED + "Invalid input." + RESET)

    if not player.inventory:
        print("Inventory empty. Leaving store.")



# INVENTORY


def show_inventory(player: Player) -> None:
    print(CYAN + "\n🎒 INVENTORY (sorted by rarity & value)" + RESET)
    if not player.inventory:
        print("  Empty.")
        return
    counts: dict[str, int] = {}
    sorted_inv = player.sorted_inventory()
    for item in sorted_inv:
        key = str(item)
        counts[key] = counts.get(key, 0) + 1
    seen: set[str] = set()
    for item in sorted_inv:
        key = str(item)
        if key not in seen:
            seen.add(key)
            suffix = f" x{counts[key]}" if counts[key] > 1 else ""
            print(f"  {item}{suffix}")


# PHASE 4 — STATS SCREEN


def show_stats(player: Player) -> None:
    from classes import COMMON_POOL, RARE_POOL, ULTRA_POOL

    history = player.spin_history
    total   = len(history)

    print(CYAN + "\n📊 SESSION STATS" + RESET)
    print("=" * 44)

    # ── General ───────────────────────────────
    print(f"  Total Spins    : {player.spin_count}")
    print(f"  Current Points : {player.points}")
    print(f"  Inventory Size : {len(player.inventory)}")

    if total == 0:
        print("  No spins yet.")
        print("=" * 44)
        return

    # ── Drop counts & rates ───────────────────
    commons = sum(1 for h in history if h["rarity"] == "Common")
    rares   = sum(1 for h in history if h["rarity"] == "Rare")
    ultras  = sum(1 for h in history if h["rarity"] == "Ultra Rare")

    print(f"\n  ── Drop Rates (actual) ──")
    print(GREEN  + f"    Common     : {commons:>3} pulls  ({commons/total*100:.1f}%)" + RESET)
    print(PURPLE + f"    Rare       : {rares:>3} pulls  ({rares/total*100:.1f}%)"     + RESET)
    print(YELLOW + f"    Ultra Rare : {ultras:>3} pulls  ({ultras/total*100:.1f}%)"   + RESET)

    if ultras > 0:
        print(f"\n  Avg spins per Ultra Rare : {total/ultras:.1f}")
    guaranteed = sum(1 for h in history if h.get("guaranteed"))
    if guaranteed:
        print(f"  Pity triggers            : {guaranteed}")

    # ── Collection progress ───────────────────
    pool_sizes   = {"Common": len(COMMON_POOL), "Rare": len(RARE_POOL), "Ultra Rare": len(ULTRA_POOL)}
    ever_pulled  = {h["item_name"] for h in history}   # unique item names ever received

    common_pool_names = {item.name for item in COMMON_POOL}
    rare_pool_names   = {item.name for item in RARE_POOL}
    ultra_pool_names  = {item.name for item in ULTRA_POOL}

    common_found = len(ever_pulled & common_pool_names)
    rare_found   = len(ever_pulled & rare_pool_names)
    ultra_found  = len(ever_pulled & ultra_pool_names)

    print(f"\n  ── Collection Progress ──")
    print(GREEN  + f"    Common     : {common_found}/{pool_sizes['Common']} unique items discovered" + RESET)
    print(PURPLE + f"    Rare       : {rare_found}/{pool_sizes['Rare']} unique items discovered"     + RESET)
    print(YELLOW + f"    Ultra Rare : {ultra_found}/{pool_sizes['Ultra Rare']} unique items discovered" + RESET)

    total_found = common_found + rare_found + ultra_found
    total_pool  = sum(pool_sizes.values())
    print(f"    Overall    : {total_found}/{total_pool} items in the game found")

    # ── Full item history ─────────────────────
    print(f"\n  ── Every Item Ever Pulled ──")

    # Count how many times each item was pulled, grouped by rarity
    item_counts: dict[str, int] = {}
    item_rarity: dict[str, str] = {}
    for h in history:
        name = h["item_name"]
        item_counts[name] = item_counts.get(name, 0) + 1
        item_rarity[name] = h["rarity"]

    # Print grouped by rarity order
    for rarity, color, pool_names in [
        ("Ultra Rare", YELLOW, ultra_pool_names),
        ("Rare",       PURPLE, rare_pool_names),
        ("Common",     GREEN,  common_pool_names),
    ]:
        items_in_group = [(name, item_counts[name])
                          for name in item_counts if item_rarity[name] == rarity]
        if not items_in_group:
            continue
        items_in_group.sort(key=lambda x: -x[1])   # most pulled first
        print(color + f"\n    [{rarity}]" + RESET)
        for name, count in items_in_group:
            bar = "█" * min(count, 20)
            print(color + f"      {name:<22} x{count:<3}  {bar}" + RESET)

    print("\n" + "=" * 44)



# BANNER SELECTION


def select_banner() -> Banner:
    print(CYAN + "\n🎰 SELECT A BANNER" + RESET)
    for i, banner in enumerate(BANNERS, 1):
        print(f"  {i}. {banner}")
    while True:
        choice = input("Banner number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(BANNERS):
            selected = BANNERS[int(choice) - 1]
            print(GREEN + f"Selected: {selected.name}" + RESET)
            return selected
        print(RED + "Invalid choice." + RESET)



# GAME LOOP


def play_game(player: Player, banner: Banner) -> None:
    has_pity = isinstance(banner, StandardBanner)

    while True:

        if player.is_broke():
            print(RED + "\n💀 GAME OVER! 💀" + RESET)
            print("No points and no items to sell.")
            break

        print(f"\n💰 Points: {player.points}  |  Spins: {player.spin_count}  |  "
              f"URs: {player.ultra_rare_count()}")

        if has_pity:
            pity_bar(player.pity_counter)
        else:
            print(CYAN + f"Banner: {banner.name} — no pity system" + RESET)

        print("[Enter=1 Spin | 5=Spin×5 | 0=Spin×10 | "
              "s=Store | i=Inventory | t=Stats | q=Save & Quit]")
        command = input("Your choice: ").lower().strip()

        # ── SPIN ──────────────────────────────────
        if command in ("", "5", "0"):
            spin_amount = {"": 1, "5": 5, "0": 10}[command]

            for _ in range(spin_amount):
                spin_animation()

                if not player.spend_points(10):
                    print(RED + "Not enough points!" + RESET)
                    break

                player.spin_count   += 1
                player.pity_counter += 1

                rarity, guaranteed = banner.spin(player.pity_counter)

                if rarity == "Ultra Rare":
                    player.pity_counter = 0

                item = get_random_item(rarity)
                player.add_item(item)
                player.record_spin(rarity, item.name, guaranteed)

                print(f"  → {item}")

                if guaranteed:
                    print(YELLOW + "  ✨ 75-SPIN GUARANTEE TRIGGERED! ✨" + RESET)

                bonus_event(player)

        elif command == "s":
            open_store(player)

        elif command == "i":
            show_inventory(player)

        elif command == "t":
            show_stats(player)

        elif command == "q":
            save_player(player)
            update_leaderboard(player, banner.name)
            show_leaderboard()
            break

        else:
            print(RED + "Invalid command." + RESET)

    print(f"\nTotal spins   : {player.spin_count}")
    print(f"Final points  : {player.points}")
    print(f"Ultra Rares   : {player.ultra_rare_count()}")
    print("-" * 40)


# STARTUP (save / load)


def startup() -> Player:
    """Offer to resume a saved session, or start fresh."""
    saved = load_player()
    if saved:
        print(CYAN + "\n💾 Saved game found!" + RESET)
        print(f"  Points: {saved.points}  |  Spins: {saved.spin_count}  |  "
              f"Items: {len(saved.inventory)}  |  URs: {saved.ultra_rare_count()}")
        if input("Continue saved game? (y/n): ").lower().strip() == "y":
            delete_save()
            return saved
    return Player()


# MAIN


def main() -> None:
    display_intro()
    show_leaderboard()

    play_again = "y"
    while play_again == "y":
        player = startup()
        banner = select_banner()
        play_game(player, banner)
        play_again = input("\nPlay again? (y/n): ").lower().strip()

    print("Thanks for playing! 👋")


main()
