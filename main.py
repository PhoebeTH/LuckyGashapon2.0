"""
Lucky Gashapon 2.0
Lucky Gachapon is a spin-based item collecting game. 
The player starts with 150 points and spends 10 per spin to earn Common, Rare, or Ultra Rare items. 
Items can be sold to keep spinning. Choose between the Standard Banner (with a 75-spin pity guarantee) or the Bonus Banner (free rolls, lower sell value). Manage your economy by selling items back to the store, chase Ultra Rares, and track your full collection progress. 
**New Game+ mode that challenges you to collect every item in the game as fast as possible

Thunyapron Thianpramook (Phoebe)
June 09, 2026
"""

import random
import time
import os
import json

from classes import (
    GREEN, PURPLE, YELLOW, CYAN, RED, RESET,
    Item, Player, Banner, StandardBanner, BonusBanner,
    item_from_dict, get_random_item, BANNERS,
    COMMON_POOL, RARE_POOL, ULTRA_POOL,
    BONUS_COMMON_POOL, BONUS_RARE_POOL, BONUS_ULTRA_POOL,
    ALL_ITEMS, TOTAL_UNIQUE_ITEMS,
    sfx_spin, sfx_rare, sfx_ultra,
    sfx_sell, sfx_bonus, sfx_gameover,
    validate_price, _init_audio,
)

SAVE_FILE        = "save.json"
LEADERBOARD_FILE = "leaderboard.json"


# ── FILE I/O ──────────────────────────────────────────────────────────────────

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
 
    board = load_leaderboard()
    entry: dict = {
        "ultra_rares": player.ultra_rare_count(),
        "spins":       player.spin_count,
        "points":      player.points,
        "banner":      banner_name,
    }
    if player.ng_plus_record is not None:
        entry["ng_plus_record"] = player.ng_plus_record
    board.append(entry)
    board.sort(key=lambda x: x["ultra_rares"], reverse=True)
    board = board[:5]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)


def show_leaderboard() -> None:
    board = load_leaderboard()
    print(YELLOW + "\n🏆 TOP 5 LEADERBOARD  (by Ultra Rares pulled)" + RESET)
    print("─" * 60)
    if not board:
        print("  No sessions recorded yet.")
    else:
        for rank, entry in enumerate(board, 1):
            ng_tag = ""
            if "ng_plus_record" in entry:
                ng_tag = f"  {CYAN}[NG+ best: {entry['ng_plus_record']} spins]{RESET}"
            print(f"  {rank}. {YELLOW}{entry['ultra_rares']} URs{RESET}  |  "
                  f"{entry['spins']} spins  |  "
                  f"{entry['points']} pts  |  "
                  f"{CYAN}{entry['banner']}{RESET}{ng_tag}")
    print("─" * 60)


# ── ASCII ART ─────────────────────────────────────────────────────────────────

def draw_logo() -> None:
    logo = r"""
 ██╗     ██╗   ██╗ ██████╗██╗  ██╗██╗   ██╗
 ██║     ██║   ██║██╔════╝██║ ██╔╝╚██╗ ██╔╝
 ██║     ██║   ██║██║     █████╔╝  ╚████╔╝
 ██║     ██║   ██║██║     ██╔═██╗   ╚██╔╝
 ███████╗╚██████╔╝╚██████╗██║  ██╗   ██║
 ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝   ╚═╝
  ██████╗  █████╗  ██████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ███╗   ██╗
 ██╔════╝ ██╔══██╗██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗████╗  ██║
 ██║  ███╗███████║██║     ███████║███████║██████╔╝██║   ██║██╔██╗ ██║
 ██║   ██║██╔══██║██║     ██╔══██║██╔══██║██╔═══╝ ██║   ██║██║╚██╗██║
 ╚██████╔╝██║  ██║╚██████╗██║  ██║██║  ██║██║     ╚██████╔╝██║ ╚████║
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═══╝
"""
    colors = [RED, YELLOW, GREEN, CYAN, PURPLE, RED, YELLOW, GREEN, CYAN, PURPLE, RED, YELLOW]
    for i, line in enumerate(logo.splitlines()):
        print(colors[i % len(colors)] + line + RESET)


def draw_gameover_art() -> None:
    art = r"""
   ██████╗  █████╗ ███╗   ███╗███████╗     ██████╗ ██╗   ██╗███████╗██████╗
  ██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔═══██╗██║   ██║██╔════╝██╔══██╗
  ██║  ███╗███████║██╔████╔██║█████╗      ██║   ██║██║   ██║█████╗  ██████╔╝
  ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
  ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝     ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
"""
    for line in art.splitlines():
        print(RED + line + RESET)


def draw_ultra_rare_art() -> None:
    art = r"""
    *    .  *       .        *    .
  . *  ✨✨✨✨✨✨✨✨✨  *  .
    ✨   ★  U L T R A  ★    ✨
    ✨    ★  R  A  R  E  ★  ✨
  . *  ✨✨✨✨✨✨✨✨✨  *  .
    *    .  *       .        *    .
"""
    for line in art.splitlines():
        print(YELLOW + line + RESET)


def draw_ng_plus_art() -> None:
    art = r"""
  ███╗   ██╗███████╗██╗    ██╗     ██████╗  █████╗ ███╗   ███╗███████╗ ██╗
  ████╗  ██║██╔════╝██║    ██║    ██╔════╝ ██╔══██╗████╗ ████║██╔════╝ ██║
  ██╔██╗ ██║█████╗  ██║ █╗ ██║    ██║  ███╗███████║██╔████╔██║█████╗  ██╔╝
  ██║╚██╗██║██╔══╝  ██║███╗██║    ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  ╚═╝
  ██║ ╚████║███████╗╚███╔███╔╝    ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗ ██╗
  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝      ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝ ╚═╝
"""
    for line in art.splitlines():
        print(CYAN + line + RESET)


# ── DISPLAY HELPERS ───────────────────────────────────────────────────────────

def display_intro() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    draw_logo()
    print()
    print(YELLOW + "  Ultra Rare drop rate : 0.5%   🌟")
    print(PURPLE + "  Rare drop rate       : 14.5%  💎")
    print(GREEN  + "  Common drop rate     : 85%    🪙")
    print(RED    + "  UR GUARANTEED at 75 spins (Standard Banner only)!" + RESET)
    print(f"\n  Start with {CYAN}150 points{RESET}. Standard spins cost {YELLOW}10 pts{RESET}. Bonus Banner is {GREEN}FREE{RESET}!")
    print("─" * 50)


def pity_bar(pity: int, max_pity: int = 75) -> None:
    total  = 20
    filled = int(pity * total / max_pity)
    bar    = "█" * filled + "░" * (total - filled)
    print(PURPLE + f"  Pity: [{bar}] {pity}/{max_pity}" + RESET)


def collection_bar(player: Player) -> None:
    """Show overall collection progress inline."""
    found  = len(player.unique_items_ever_pulled() & ALL_ITEMS)
    total  = TOTAL_UNIQUE_ITEMS
    pct    = found / total
    filled = int(pct * 20)
    bar    = "█" * filled + "░" * (20 - filled)
    print(GREEN + f"  Dex:  [{bar}] {found}/{total} items" + RESET)


def spin_animation() -> None:
    sfx_spin()
    print("  Spinning", end="")
    for _ in range(3):
        time.sleep(0.15)
        print(".", end="", flush=True)
    print()


def bonus_event(player: Player) -> None:
    if random.random() < 0.12:      # slightly more frequent (12% vs 10%)
        sfx_bonus()
        bonus = random.randint(5, 15)
        print(CYAN + f"  🎁 BONUS! +{bonus} points!" + RESET)
        player.earn_points(bonus)


# ── STORE ─────────────────────────────────────────────────────────────────────

def _item_sell_value(item: Item) -> int:
 
    raw = item.get_value()
    if item.banner_tag == "(B2)":
        return max(1, int(raw * 0.60))
    return raw


def open_store(player: Player, banner: "Banner | None" = None) -> None:
    while player.inventory:
        print(CYAN + "\n  🛒 STORE — Sell Items" + RESET)
        if banner and isinstance(banner, BonusBanner):
            print(YELLOW + "  ⚠ B2 items sell at 60% value." + RESET)
        sorted_inv = player.sorted_inventory()
        for i, item in enumerate(sorted_inv, 1):
            print(f"  {i}. {item}")

        print("\n  Type item numbers (example: 1 2 3)")
        print("  a = sell everything  |  e = exit store")
        choice = input("  Choice: ").lower().strip()

        if choice == "e":
            break

        elif choice == "a":
            total = sum(_item_sell_value(item) for item in player.inventory)
            player.inventory.clear()
            player.earn_points(total)
            sfx_sell()
            print(CYAN + f"  Sold EVERYTHING for {total} points! 💰" + RESET)

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
                            sell_val = _item_sell_value(item)
                            total_value += sell_val
                            print(f"  Sold {item}  → {sell_val} pts 💰")
                player.earn_points(total_value)
                if total_value:
                    sfx_sell()
                    print(CYAN + f"  Total gained: {total_value} points! 💰" + RESET)
            else:
                print(RED + "  Invalid input." + RESET)

    if not player.inventory:
        print("  Inventory empty. Leaving store.")


# ── INVENTORY (now shows collection + history) ────────────────────────────────

def show_inventory(player: Player) -> None:
    
    os.system("cls" if os.name == "nt" else "clear")

    # ── Current items in bag ──────────────────
    print(CYAN + "\n  🎒 CURRENT INVENTORY  (sorted by rarity & value)" + RESET)
    print("─" * 50)
    if not player.inventory:
        print("  Empty.")
    else:
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

    # ── Collection Progress ───────────────────
    print()
    print(CYAN + "  📖 COLLECTION PROGRESS" + RESET)
    print("─" * 50)

    ever_pulled = player.unique_items_ever_pulled()

    all_common_names  = {i.name for i in COMMON_POOL}  | {i.name for i in BONUS_COMMON_POOL}
    all_rare_names    = {i.name for i in RARE_POOL}    | {i.name for i in BONUS_RARE_POOL}
    all_ultra_names   = {i.name for i in ULTRA_POOL}   | {i.name for i in BONUS_ULTRA_POOL}

    c_found = len(ever_pulled & all_common_names)
    r_found = len(ever_pulled & all_rare_names)
    u_found = len(ever_pulled & all_ultra_names)
    c_total = len(all_common_names)
    r_total = len(all_rare_names)
    u_total = len(all_ultra_names)

    def _prog_bar(found: int, total: int) -> str:
        filled = int(found / total * 15)
        return "█" * filled + "░" * (15 - filled)

    print(GREEN  + f"    Common     : [{_prog_bar(c_found, c_total)}] {c_found}/{c_total}" + RESET)
    print(PURPLE + f"    Rare       : [{_prog_bar(r_found, r_total)}] {r_found}/{r_total}" + RESET)
    print(YELLOW + f"    Ultra Rare : [{_prog_bar(u_found, u_total)}] {u_found}/{u_total}" + RESET)

    total_found = c_found + r_found + u_found
    total_pool  = c_total + r_total + u_total
    print(f"    Overall    : {total_found}/{total_pool} unique items discovered")

    # ── Every item ever pulled ────────────────
    history = player.spin_history
    if history:
        print()
        print(CYAN + "  📜 EVERY ITEM EVER PULLED" + RESET)
        print("─" * 50)

        item_counts: dict[str, int] = {}
        item_rarity: dict[str, str] = {}
        for h in history:
            name = h["item_name"]
            item_counts[name] = item_counts.get(name, 0) + 1
            item_rarity[name] = h["rarity"]

        for rarity, color, pool_names in [
            ("Ultra Rare", YELLOW, all_ultra_names),
            ("Rare",       PURPLE, all_rare_names),
            ("Common",     GREEN,  all_common_names),
        ]:
            items_in_group = [(name, item_counts[name])
                              for name in item_counts if item_rarity[name] == rarity]
            if not items_in_group:
                continue
            items_in_group.sort(key=lambda x: -x[1])
            print(color + f"\n    [{rarity}]" + RESET)
            for name, count in items_in_group:
                bar = "█" * min(count, 20)
                print(color + f"      {name:<24} x{count:<3}  {bar}" + RESET)

    input(CYAN + "\n  [Press Enter to return]" + RESET)


# ── STATS ─────────────────────────────────────────────────────────────────────

def show_stats(player: Player) -> None:
    history = player.spin_history
    total   = len(history)

    print(CYAN + "\n  📊 SESSION STATS" + RESET)
    print("═" * 48)
    print(f"  Total Spins    : {player.spin_count}")
    print(f"  Current Points : {player.points}")
    print(f"  Inventory Size : {len(player.inventory)}")

    if player.ng_plus_active:
        print(CYAN + f"  NG+ Spins Used : {player.ng_plus_spins_used()}" + RESET)
        if player.ng_plus_record:
            print(CYAN + f"  NG+ Record     : {player.ng_plus_record} spins" + RESET)

    if total == 0:
        print("  No spins yet.")
        print("═" * 48)
        return

    # ── Per-banner breakdown ──────────────────
   
    seen_banners: list[str] = []
    for h in history:
        bn = h.get("banner_name", "Unknown")
        if bn not in seen_banners:
            seen_banners.append(bn)

    for banner_name in seen_banners:
        banner_hist = [h for h in history if h.get("banner_name", "Unknown") == banner_name]
        b_total  = len(banner_hist)
        commons  = sum(1 for h in banner_hist if h["rarity"] == "Common")
        rares    = sum(1 for h in banner_hist if h["rarity"] == "Rare")
        ultras   = sum(1 for h in banner_hist if h["rarity"] == "Ultra Rare")

        print(f"\n  ── {CYAN}{banner_name}{RESET}  ({b_total} spins) ──")
        print(GREEN  + f"    Common     : {commons:>3} pulls  ({commons/b_total*100:.1f}%)" + RESET)
        print(PURPLE + f"    Rare       : {rares:>3} pulls  ({rares/b_total*100:.1f}%)"     + RESET)
        print(YELLOW + f"    Ultra Rare : {ultras:>3} pulls  ({ultras/b_total*100:.1f}%)"   + RESET)

        if ultras > 0:
            print(f"    Avg spins/UR : {b_total/ultras:.1f}")
        guaranteed = sum(1 for h in banner_hist if h.get("guaranteed"))
        if guaranteed:
            print(f"    Pity triggers: {guaranteed}")

    # ── All-banner totals (only if more than one banner used) ─────────────────
    if len(seen_banners) > 1:
        commons = sum(1 for h in history if h["rarity"] == "Common")
        rares   = sum(1 for h in history if h["rarity"] == "Rare")
        ultras  = sum(1 for h in history if h["rarity"] == "Ultra Rare")
        print(f"\n  ── {YELLOW}ALL BANNERS COMBINED{RESET}  ({total} spins) ──")
        print(GREEN  + f"    Common     : {commons:>3} pulls  ({commons/total*100:.1f}%)" + RESET)
        print(PURPLE + f"    Rare       : {rares:>3} pulls  ({rares/total*100:.1f}%)"     + RESET)
        print(YELLOW + f"    Ultra Rare : {ultras:>3} pulls  ({ultras/total*100:.1f}%)"   + RESET)
        if ultras > 0:
            print(f"    Avg spins/UR : {total/ultras:.1f}")

    print("\n" + "═" * 48)


# ── BANNER SELECTION ──────────────────────────────────────────────────────────

def select_banner() -> "Banner":
    print(CYAN + "\n  🎰 SELECT A BANNER" + RESET)
    for i, banner in enumerate(BANNERS, 1):
        print(f"  {i}. {banner}")
    while True:
        choice = input("  Banner number: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(BANNERS):
            selected = BANNERS[int(choice) - 1]
            print(GREEN + f"  Selected: {selected.name}" + RESET)
            return selected
        print(RED + "  Invalid choice." + RESET)


# ── NG+ CHECK ─────────────────────────────────────────────────────────────────

def check_ng_plus(player: Player, banner: "Banner") -> None:
    """If collection is complete, offer NG+ mode."""
    if not player.collection_complete():
        return
    if player.ng_plus_active:
        # Already in NG+ — record and congratulate
        spins_used = player.ng_plus_spins_used()
        draw_ng_plus_art()
        print(YELLOW + f"  🏆 COLLECTION COMPLETE AGAIN in {spins_used} NG+ spins!" + RESET)
        if player.ng_plus_record is None or spins_used < player.ng_plus_record:
            player.ng_plus_record = spins_used
            print(GREEN + "  🎉 NEW NG+ RECORD!" + RESET)
        else:
            print(f"  Best so far: {player.ng_plus_record} spins. Keep trying!")
        player.ng_plus_active = False
        return

    # First completion — offer NG+
    draw_ng_plus_art()
    print(YELLOW + "\n  🎊 YOU COLLECTED EVERY ITEM IN THE GAME! 🎊" + RESET)
    print(f"  Total spins to complete: {player.spin_count}")
    print()
    print("  ┌──────────────────────────────────────────┐")
    print("  │  NEW GAME+  Challenge Mode unlocked!     │")
    print("  │  Race to collect ALL items again         │")
    print("  │  and beat your spin count record!        │")
    print("  └──────────────────────────────────────────┘")
    ans = input("  Start NG+ now? (y/n): ").lower().strip()
    if ans == "y":
        player.ng_plus_active  = True
        player.ng_plus_start   = player.spin_count
        player.spin_history    = []   # reset pull log for NG+
        player.inventory       = []
        player.pity_counter    = 0
        print(CYAN + "  NG+ started! Collect everything as fast as you can!" + RESET)


# ── GAME LOOP ─────────────────────────────────────────────────────────────────

def play_game(player: Player, banner: "Banner") -> None:
    has_pity    = isinstance(banner, StandardBanner)
    is_bonus    = isinstance(banner, BonusBanner)
    spin_cost   = 0 if is_bonus else 10

    while True:

        if player.is_broke():
            sfx_gameover()
            draw_gameover_art()
            print(RED + "  No points and no items to sell." + RESET)
            break

        # ── HUD ──────────────────────────────────
        print()
        print(f"  💰 Points: {YELLOW}{player.points}{RESET}  |  "
              f"Spins: {player.spin_count}  |  "
              f"URs: {YELLOW}{player.ultra_rare_count()}{RESET}")

        if has_pity:
            pity_bar(player.pity_counter)
        else:
            spin_label = f"{GREEN}FREE{RESET}" if is_bonus else f"10 pts"
            print(CYAN + f"  Banner: {banner.name} — {spin_label}/spin — no pity" + RESET)

        collection_bar(player)

        if player.ng_plus_active:
            print(CYAN + f"  ⏱ NG+ spins: {player.ng_plus_spins_used()}  "
                  f"| record: {player.ng_plus_record or '—'}" + RESET)

        print()
        print("  [Enter=1 Spin | 5=Spin×5 | 0=Spin×10 | "
              "s=Store | i=Inventory | t=Stats | q=Save & Quit]")
        command = input("  Your choice: ").lower().strip()

        # ── SPIN ──────────────────────────────────
        if command in ("", "5", "0"):
            spin_amount = {"": 1, "5": 5, "0": 10}[command]

            for _ in range(spin_amount):
                spin_animation()

                if spin_cost > 0 and not player.spend_points(spin_cost):
                    print(RED + "  Not enough points!" + RESET)
                    break

                player.spin_count   += 1
                player.pity_counter += 1

                rarity, guaranteed = banner.spin(player.pity_counter)

                if rarity == "Ultra Rare":
                    player.pity_counter = 0
                    draw_ultra_rare_art()
                    sfx_ultra()
                elif rarity == "Rare":
                    sfx_rare()
                # Common: no sound

                item = get_random_item(rarity, bonus=is_bonus)
                player.add_item(item)
                player.record_spin(rarity, item.name, guaranteed, banner.name)

                print(f"  → {item}")

                if guaranteed:
                    print(YELLOW + "  ✨ 75-SPIN GUARANTEE TRIGGERED! ✨" + RESET)

                bonus_event(player)

            # Check NG+
            check_ng_plus(player, banner)

        elif command == "s":
            open_store(player, banner)

        elif command == "i":
            show_inventory(player)

        elif command == "t":
            show_stats(player)

        elif command == "q":
            sfx_gameover()
            save_player(player)
            update_leaderboard(player, banner.name)
            show_leaderboard()
            break

        else:
            print(RED + "  Invalid command." + RESET)

    print()
    print(f"  Total spins   : {player.spin_count}")
    print(f"  Final points  : {player.points}")
    print(f"  Ultra Rares   : {player.ultra_rare_count()}")
    print("─" * 40)

# ── STARTUP ───────────────────────────────────────────────────────────────────

def startup() -> "Player":
    saved = load_player()
    if saved:
        print(CYAN + "\n  💾 Saved game found!" + RESET)
        print(f"  Points: {saved.points}  |  Spins: {saved.spin_count}  |  "
              f"Items: {len(saved.inventory)}  |  URs: {saved.ultra_rare_count()}")
        if input("  Continue saved game? (y/n): ").lower().strip() == "y":
            delete_save()
            return saved
    return Player()

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main() -> None:
    _init_audio()
    display_intro()
    show_leaderboard()

    play_again = "y"
    while play_again == "y":
        player = startup()
        banner = select_banner()
        play_game(player, banner)
        play_again = input("\n  Play again? (y/n): ").lower().strip()

    print("  Thanks for playing! 👋")



if __name__ == "__main__":
    main()
