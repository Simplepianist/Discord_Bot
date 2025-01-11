"""
Dieses Modul enthält Funktionen zur Simulation eines Roulette-Spiels
unter Verwendung der Discord-Bibliothek.
"""

import asyncio
import random
from discord import Interaction
from discord.ext.commands import Context
from Util.util_commands import send_message

# Liste der Roulette-Zahlen und ihrer Farben
ROULETTE_NUMBERS = [
    (0, "green"), (32, "red"), (15, "black"), (19, "red"), (4, "black"),
    (21, "red"), (2, "black"), (25, "red"), (17, "black"), (34, "red"),
    (6, "black"), (27, "red"), (13, "black"), (36, "red"), (11, "black"),
    (30, "red"), (8, "black"), (23, "red"), (10, "black"), (5, "red"),
    (24, "black"), (16, "red"), (33, "black"), (1, "red"), (20, "black"),
    (14, "red"), (31, "black"), (9, "red"), (22, "black"), (18, "red"),
    (29, "black"), (7, "red"), (28, "black"), (12, "red"), (35, "black"),
    (3, "red"), (26, "black"), (0, "green")
]

async def play_roulette(entry, bet_type: str, msg) -> bool:
    """
    Simuliert ein Roulette-Spiel und aktualisiert die Nachricht mit dem Ergebnis.

    Args:
        entry: Die Wette des Spielers (Zahl oder Farbe).
        bet_type (str): Der Typ der Wette ("number" oder "color").
        msg: Die Nachricht, die aktualisiert werden soll.

    Returns:
        bool: True, wenn die Wette gewonnen wurde, sonst False.
    """
    random.shuffle(ROULETTE_NUMBERS)
    winning = random.choice(ROULETTE_NUMBERS)
    if winning[1] == "green":
        await msg.edit(content=f"Landed: **{winning[0]}** :green_square:")
    elif winning[1] == "red":
        await msg.edit(content=f"Landed: **{winning[0]}** :red_square:")
    elif winning[1] == "black":
        await msg.edit(content=f"Landed: **{winning[0]}** :black_large_square:")
    if bet_type == "number":
        entry = int(entry)
        return entry == winning[0]
    if bet_type == "color":
        return entry == winning[1]

def validate_entry(entry: str):
    """
    Validiert die Eingabe des Spielers.

    Args:
        entry (str): Die Eingabe des Spielers (Zahl oder Farbe).

    Returns:
        list: Eine Liste, die angibt, ob die Eingabe gültig ist und die konvertierte Eingabe.
    """
    if entry.isdigit() and 37 > int(entry) >= 0:
        return [True, int(entry)]
    if entry.lower() in ["red", "black", "green"]:
        return [True, entry.lower()]
    return [False, None]

async def spinning(ctx: Context | Interaction):
    """
    Simuliert das Drehen des Roulette-Rads und sendet die Zwischenergebnisse.

    Args:
        ctx (Context | Interaction): Der Kontext der Discord-Nachricht.

    Returns:
        msg: Die Nachricht mit dem Endergebnis des Drehs.
    """
    msg = None
    for _ in range(4):
        spin_number, spin_color = random.choice(ROULETTE_NUMBERS)
        if msg is None:
            if spin_color == "green":
                msg = await send_message(ctx, f"Spinning... "
                                              f"**{spin_number}**  :green_square:")
            elif spin_color == "red":
                msg = await send_message(ctx, f"Spinning... "
                                              f"**{spin_number}**  :red_square:")
            elif spin_color == "black":
                msg = await send_message(ctx, f"Spinning... "
                                              f"**{spin_number}**  :black_large_square:")
        else:
            await msg.edit(content=f"Spinning... **{spin_number}** "
                                   f"{':red_square:' if spin_color == 'red'
                                   else ':black_large_square:'}")
        await asyncio.sleep(0.5)
    return msg
