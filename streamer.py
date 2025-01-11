"""
Dieses Modul enthält die Implementierung eines Discord-Bots
mit verschiedenen Befehlen und Ereignishandlern.
Der Bot verwendet die discord.py-Bibliothek und bietet Funktionen
wie das Synchronisieren von Befehlen,
das Verwalten von Benutzerkonten und das Spielen von Minispielen.

Importierte Module:
- os: Zum Zugriff auf Umgebungsvariablen.
- logging: Zum Protokollieren von Ereignissen und Fehlern.
- discord: Zum Interagieren mit der Discord-API.
- app_commands: Zum Erstellen von Anwendungsbefehlen.
- discord.ext.commands: Zum Erstellen von Befehlen und Ereignishandlern.
- Commands: Enthält verschiedene Befehlsimplementierungen.
- Util: Enthält Hilfsfunktionen und Variablen.

Konstanten:
- SHUTDOWN_INITIATED: Ein boolescher Wert, der anzeigt, ob der Shutdown-Prozess initiiert wurde.

Funktionen:
- on_ready: Wird aufgerufen, wenn der Bot bereit ist.
- on_command_error: Wird aufgerufen, wenn ein Fehler bei der Befehlsausführung auftritt.
- clear_commands: Löscht alle Befehle aus dem Befehlsbaum.
- load_commands: Synchronisiert die Befehle mit dem Befehlsbaum.
- _setMoney: Setzt das Geld eines Benutzers.
- _shutdown: Fährt den Bot herunter.
- _reset: Setzt den Status des Bots zurück.
- _setStatus: Setzt den Status des Bots.
- _help: Zeigt das Hilfemenü an.
- _rules: Zeigt die Regeln an.
- _aliases: Zeigt die Aliasliste der Befehle an.
- _ping: Antwortet mit "Pong".
- _invite: Gibt den Einladungslink für den Server aus.
- _stream: Gibt den Streamlink von Simplebox aus.
- _scoreboard: Zeigt das Scoreboard für die meisten Coins an.
- _daily: Führt den täglichen Befehl aus.
- _send: Sendet Geld an einen anderen Benutzer.
- _money: Zeigt das Geld eines Benutzers an.
- _robbing: Führt den Raubbefehl aus.
- _blackjack: Spielt eine Runde Blackjack.
- _roulette: Spielt eine Runde Roulette.
- _higherLower: Spielt eine Runde Higher/Lower.
- _quote: Gibt ein zufälliges Anime-Zitat aus.
- _qotd: Gibt das Zitat des Tages aus.
- rules: Zeigt die Regeln der Spiele an.
- aliases: Zeigt die Aliasliste aller Befehle an.
- ping: Antwortet mit "Pong".
- invite: Gibt den Einladungslink für den Server aus.
- stream: Gibt den Streamlink von Simplebox aus.
- scoreboard: Zeigt das Scoreboard für die Games an.
- daily: Führt den täglichen Befehl aus.
- send: Sendet Geld an einen anderen Benutzer.
- money: Zeigt das Geld eines Benutzers an.
- blackjack: Spielt eine Runde Blackjack.
- roulette: Spielt eine Runde Roulette.
- higher_lower: Spielt eine Runde Higher/Lower.
- robbing: Führt den Raubbefehl aus.
- quote: Gibt ein zufälliges Anime-Zitat aus.
- qotd: Gibt das Zitat des Tages aus.
"""
import os
import logging

from discord import Streaming, Member
from discord import app_commands, Interaction
from discord.app_commands import CommandInvokeError, CommandOnCooldown
from discord.ext.commands import Context, is_owner, BadArgument, MissingRequiredArgument, \
    CheckFailure, NotOwner
from Commands.admin_commands import (set_money_command, shutdown_command, reset_status_command,
                                     set_status_command)
from Commands.game_commands import (scoreboard_command, daily_command, send_command, money_command,
                                    rob_command, blackjack_command,
                                    roulette_command, higher_lower_command)
from Commands.main_commands import (help_command, rules_command, alias_command, ping_command,
                                    invite_command, stream_command)
from Commands.social_commands import anime_quote, qotd_command
from Util import variables
from Util.variables import streamURL
from Util.util_commands import db, execute_gaming_with_timeout, send_message
from Util.variables import bot


@bot.event
async def on_ready():
    """
    Diese Funktion wird aufgerufen, wenn der Bot bereit ist.
    Sie initialisiert die Datenbankverbindung, konfiguriert das Logging,
    synchronisiert die Befehle und setzt den Status des Bots.

    Aktionen:
    - Initialisiert den Datenbank-Pool.
    - Konfiguriert das Logging mit einem bestimmten Format und speichert die Logs in einer Datei.
    - Synchronisiert die Befehle des Bots.
    - Setzt den Besitzer des Bots.
    - Ändert die Präsenz des Bots zu einem Streaming-Status mit einem bestimmten Namen und URL.
    """
    await db.init_pool()
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    await bot.tree.sync()
    logging.info("Sync gestartet (1h)")
    await bot.change_presence(activity=Streaming(name=".help", url=streamURL))

@bot.event
async def on_command_error(ctx: Context, error):
    if isinstance(error, BadArgument):
        await send_message(ctx, "Falsche Angabe von Argumenten", delete_after=5)
    elif isinstance(error, MissingRequiredArgument):
        await send_message(ctx, "Fehlende Argumente", delete_after=5)
    elif isinstance(error, (CheckFailure, NotOwner)):
        await send_message(ctx, "Du hast nicht die Berechtigung, diesen Befehl auszuführen",
                           delete_after=5)
    elif isinstance(error, CommandInvokeError):
        await send_message(ctx, "Ein Fehler ist bei der Ausführung des Befehls aufgetreten",
                           delete_after=5)
    elif isinstance(error, CommandOnCooldown):
        await send_message(ctx, f"Dieser Befehl ist auf Abklingzeit. "
                                f"Versuche es in {error.retry_after:.2f} Sekunden erneut.",
                           delete_after=5)
    else:
        logging.error("Error: %s (caused by %s)", error, ctx.author.global_name)

#region .-Commands
@bot.command(name="clear")
@is_owner()
async def clear_commands(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um alle Befehle aus dem Befehlsbaum zu löschen.
    Nur der Besitzer des Bots kann diesen Befehl ausführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Protokolliert, dass der Clear-Befehl ausgelöst wurde.
    - Löscht alle Befehle aus dem Befehlsbaum.
    - Sendet eine Nachricht, dass der Befehlsbaum gelöscht wurde.
    """
    logging.info("Clear triggered by %s", ctx.author.global_name)
    bot.tree.clear_commands(guild=None)
    await ctx.channel.send("Clearing Tree")


@bot.command(name="load", aliases=['sync'])
@is_owner()
async def load_commands(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um die Befehle des Bots zu synchronisieren.
    Nur der Besitzer des Bots kann diesen Befehl ausführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Protokolliert, dass der Sync-Befehl ausgelöst wurde.
    - Synchronisiert die Befehle des Bots.
    - Sendet eine Nachricht, dass die Befehle geladen wurden.
    """
    logging.info("Sync triggered by %s", ctx.author.global_name)
    await bot.tree.sync()
    await ctx.channel.send("Loaded Commands (May be seen in 1h)")


@bot.command(name="set")
@is_owner()
async def set_money(ctx: Context | Interaction, member: Member, user_money=None):
    """
    Diese Funktion wird aufgerufen, um das Geld eines Benutzers zu setzen.
    Nur der Besitzer des Bots kann diesen Befehl ausführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - member (Member): Der Benutzer, dessen Geld gesetzt werden soll.
    - user_money (optional): Der Betrag, der gesetzt werden soll. Wenn nicht angegeben,
    wird ein Standardwert verwendet.

    Aktionen:
    - Ruft die Funktion `set_money_command` auf, um das Geld des Benutzers zu setzen.
    """
    await set_money_command(ctx, member, user_money)


# noinspection PyUnusedLocal
@bot.command(aliases=["quit", "close", "stop"])
@is_owner()
async def shutdown(_: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den Bot herunterzufahren.
    Nur der Besitzer des Bots kann diesen Befehl ausführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Setzt die globale Variable `SHUTDOWN_INITIATED` auf True.
    - Ruft die Funktion `shutdown_command` auf, um den Bot herunterzufahren.
    """
    variables.SHUTDOWN_INITIATED = True
    await shutdown_command()


@bot.command(name="reset")
@is_owner()
async def reset(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den Status des Bots zurückzusetzen.
    Nur der Besitzer des Bots kann diesen Befehl ausführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `reset_status_command` auf, um den Status des Bots zurückzusetzen.
    """
    await reset_status_command(ctx)


@bot.command(name="setStatus")
@is_owner()
async def set_status(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den Status des Bots zu setzen.
    Nur der Besitzer des Bots kann diesen Befehl ausführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `set_status_command` auf, um den Status des Bots zu setzen.
    """
    await set_status_command(ctx)


@bot.tree.command(name="help", description="Gives you the Help-Menu")
async def help_menu_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um das Hilfemenü anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `help_command` auf, um das Hilfemenü anzuzeigen.
    """
    await help_command(ctx)


@bot.command(name="help", aliases=["h"],)
async def help_menu(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um das Hilfemenü anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `help_command` auf, um das Hilfemenü anzuzeigen.
    """
    await help_command(ctx)


@bot.command(name="rule", aliases=["rules"])
async def rules(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um die Regeln anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `rules_command` auf, um die Regeln anzuzeigen.
    """
    await rules_command(ctx)


@bot.command(name="alias", aliases=["a"], description="Aliasliste der Befehle")
async def aliases(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um die Aliasliste der Befehle anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `alias_command` auf, um die Aliasliste der Befehle anzuzeigen.
    """
    await alias_command(ctx)


@bot.command(name="ping", description="Pong")
async def ping(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um auf den Ping-Befehl zu antworten.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `ping_command` auf, um mit "Pong" zu antworten.
    """
    await ping_command(ctx)


@bot.command(name="invite", aliases=["i"], description="Invite-link für diesen Server")
async def invite(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den Einladungslink für den Server anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `invite_command` auf, um den Einladungslink anzuzeigen.
    """
    await invite_command(ctx)


@bot.command(name="stream", aliases=["s"], description="Streamlink von Simplebox")
async def stream(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den Streamlink von Simplebox anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `stream_command` auf, um den Streamlink anzuzeigen.
    """
    await stream_command(ctx)


@bot.command(name="scoreboard", aliases=["sc"], description="Scoreboard für die meisten :coin:")
async def scoreboard(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um das Scoreboard für die meisten Coins anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `scoreboard_command` auf, um das Scoreboard anzuzeigen.
    """
    await scoreboard_command(ctx)


@bot.command(name="daily")
async def daily(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den täglichen Befehl auszuführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `daily_command` auf, um den täglichen Befehl auszuführen.
    """
    await daily_command(ctx)


@bot.command(name="send", aliases=["give"])
async def send(ctx: Context | Interaction, member: Member, money_to_set: int = None):
    """
    Diese Funktion wird aufgerufen, um Geld an einen anderen Benutzer zu senden.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - member (Member): Der Benutzer, der das Geld erhalten soll.
    - set_money (int, optional): Der Betrag, der gesendet werden soll. Standardmäßig None.

    Aktionen:
    - Ruft die Funktion `send_command` auf, um das Geld zu senden.
    """
    await send_command(ctx, member, money_to_set)


@bot.command(name="money", aliases=["bal"])
async def money(ctx: Context | Interaction, may_member: Member = None):
    """
    Diese Funktion wird aufgerufen, um das Geld eines Benutzers anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - may_member (Member, optional): Der Benutzer, dessen Geld angezeigt werden soll.
    Standardmäßig None.

    Aktionen:
    - Ruft die Funktion `money_command` auf, um das Geld des Benutzers anzuzeigen.
    """
    await money_command(ctx, may_member)

@bot.command(name="rob")
async def robbing(ctx: Context | Interaction, may_member: Member = None):
    """
    Diese Funktion wird aufgerufen, um den Raubbefehl auszuführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - may_member (Member, optional): Der Benutzer, der ausgeraubt werden soll. Standardmäßig None.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um den Raubbefehl auszuführen.
    """
    await execute_gaming_with_timeout(ctx, rob_command, may_member)

@bot.command(name="blackjack", aliases=["bj"])
async def blackjack(ctx: Context | Interaction, bet: int):
    """
    Diese Funktion wird aufgerufen, um eine Runde Blackjack zu spielen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - bet (int): Der Einsatzbetrag für das Spiel.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Blackjack zu spielen.
    """
    await execute_gaming_with_timeout(ctx, blackjack_command, bet)

@bot.command(name="roulette", aliases=["rl"])
async def roulette(ctx: Context | Interaction, bet: int, entry: str):
    """
    Diese Funktion wird aufgerufen, um eine Runde Roulette zu spielen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - bet (int): Der Einsatzbetrag für das Spiel.
    - entry (str): Die Wette, die der Benutzer platzieren möchte.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Roulette zu spielen.
    """
    await execute_gaming_with_timeout(ctx, roulette_command, bet, entry)

@bot.command(name="higher low", aliases=["hl", "higherlower"])
async def higher_lower(ctx: Context | Interaction, bet: int):
    """
    Diese Funktion wird aufgerufen, um eine Runde Higher/Lower zu spielen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - bet (int): Der Einsatzbetrag für das Spiel.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Higher/Lower zu spielen.
    """
    await execute_gaming_with_timeout(ctx, higher_lower_command, bet)


@bot.command(name="quote")
async def quote(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um ein zufälliges Anime-Zitat auszugeben.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `anime_quote` auf, um ein zufälliges Anime-Zitat auszugeben.
    """
    await anime_quote(ctx)


@bot.command(name="qotd")
async def qotd(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um das Zitat des Tages auszugeben.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `qotd_command` auf, um das Zitat des Tages auszugeben.
    """
    await qotd_command(ctx)
#endregion

#region Tree-Commands
@bot.tree.command(name="rules", description="Hier findest du Regeln der Spiele")
async def rules_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um die Regeln der Spiele anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `rules_command` auf, um die Regeln anzuzeigen.
    """
    await rules_command(ctx)


@bot.tree.command(name="alias", description="Aliasliste aller Befehle")
async def aliases_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um die Aliasliste aller Befehle anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `alias_command` auf, um die Aliasliste anzuzeigen.
    """
    await alias_command(ctx)


@bot.tree.command(name="ping", description="Pong")
async def ping_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um auf den Ping-Befehl zu antworten.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `ping_command` auf, um mit "Pong" zu antworten.
    """
    await ping_command(ctx)


@bot.tree.command(name="invite", description="Invite-link für diesen Server")
async def invite_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den Einladungslink für den Server anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `invite_command` auf, um den Einladungslink anzuzeigen.
    """
    await invite_command(ctx)


@bot.tree.command(name="stream", description="Streamlink von Simplebox")
async def stream_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den Streamlink von Simplebox anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `stream_command` auf, um den Streamlink anzuzeigen.
    """
    await stream_command(ctx)


@bot.tree.command(name="scoreboard", description="Scoreboard für die Games")
async def scoreboard_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um das Scoreboard für die Games anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `scoreboard_command` auf, um das Scoreboard anzuzeigen.
    """
    await scoreboard_command(ctx)


@bot.tree.command(name="daily", description="Gönn dir dein Daily")
async def daily_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um den täglichen Befehl auszuführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `daily_command` auf, um den täglichen Befehl auszuführen.
    """
    await daily_command(ctx)


@bot.tree.command(name="send", description="Gib Geld an andere")
@app_commands.describe(member="Person die Geld bekommt")
@app_commands.rename(member="person")
@app_commands.describe(money_to_set="Geld das du versendest")
@app_commands.rename(money_to_set="geld")
async def send_slash(ctx: Context | Interaction, member: Member, money_to_set: int):
    """
    Diese Funktion wird aufgerufen, um Geld an einen anderen Benutzer zu senden.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - member (Member): Der Benutzer, der das Geld erhalten soll.
    - set_money (int): Der Betrag, der gesendet werden soll.

    Aktionen:
    - Ruft die Funktion `send_command` auf, um das Geld zu senden.
    """
    await send_command(ctx, member, money_to_set)


@bot.tree.command(name="money", description="Check das Geld")
@app_commands.describe(may_member="Person die du checken möchtest")
@app_commands.rename(may_member="person")
async def money_slash(ctx: Context | Interaction, may_member: Member = None):
    """
    Diese Funktion wird aufgerufen, um das Geld eines Benutzers anzuzeigen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - may_member (Member, optional): Der Benutzer, dessen Geld angezeigt werden soll.
    Standardmäßig None.

    Aktionen:
    - Ruft die Funktion `money_command` auf, um das Geld des Benutzers anzuzeigen.
    """
    await money_command(ctx, may_member)


@bot.tree.command(name="blackjack", description="Play a game of blackjack")
@app_commands.describe(bet="Wieviel du setzen möchtest")
@app_commands.rename(bet="einsatz")
async def blackjack_slash(ctx: Context | Interaction, bet: int):
    """
    Diese Funktion wird aufgerufen, um eine Runde Blackjack zu spielen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - bet (int): Der Einsatzbetrag für das Spiel.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Blackjack zu spielen.
    """
    await execute_gaming_with_timeout(ctx, blackjack_command, bet)


@bot.tree.command(name="roulette", description="Spiel ein bisschen Roulette")
@app_commands.describe(bet="Wieviel du setzen möchtest")
@app_commands.rename(bet="einsatz")
@app_commands.describe(entry="Auf was wettest du")
@app_commands.rename(entry="wettstein")
async def roulette_slash(ctx: Context | Interaction, bet: int, entry: str):
    """
    Diese Funktion wird aufgerufen, um eine Runde Roulette zu spielen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - bet (int): Der Einsatzbetrag für das Spiel.
    - entry (str): Die Wette, die der Benutzer platzieren möchte.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Roulette zu spielen.
    """
    await execute_gaming_with_timeout(ctx, roulette_command, bet, entry)

@bot.tree.command(name="higherlower", description="Spiel ein bisschen Higher/Lower")
@app_commands.describe(bet="Wieviel du setzen möchtest")
@app_commands.rename(bet="einsatz")
async def higher_lower_slash(ctx: Context | Interaction, bet: int):
    """
    Diese Funktion wird aufgerufen, um eine Runde Higher/Lower zu spielen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - bet (int): Der Einsatzbetrag für das Spiel.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um eine Runde Higher/Lower zu spielen.
    """
    await execute_gaming_with_timeout(ctx, higher_lower_command, bet)

@bot.tree.command(name="rob", description="Raube die Bank oder einen Spieler")
@app_commands.describe(may_member="Wähle eine Spieler oder Raube lieber die Bank")
@app_commands.rename(may_member="person")
async def robbing_slash(ctx: Context | Interaction, may_member: Member = None):
    """
    Diese Funktion wird aufgerufen, um den Raubbefehl auszuführen.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.
    - may_member (Member, optional): Der Benutzer, der ausgeraubt werden soll. Standardmäßig None.

    Aktionen:
    - Ruft die Funktion `execute_gaming_with_timeout` auf, um den Raubbefehl auszuführen.
    """
    await execute_gaming_with_timeout(ctx, rob_command, may_member)


@bot.tree.command(name="quote", description="Gives a random Anime Quote")
async def quote_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um ein zufälliges Anime-Zitat auszugeben.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `anime_quote` auf, um ein zufälliges Anime-Zitat auszugeben.
    """
    await anime_quote(ctx)


@bot.tree.command(name="qotd", description="Tells you the Quote of the Day")
async def qotd_slash(ctx: Context | Interaction):
    """
    Diese Funktion wird aufgerufen, um das Zitat des Tages auszugeben.

    Parameter:
    - ctx (Context | Interaction): Der Kontext, in dem der Befehl ausgeführt wurde.

    Aktionen:
    - Ruft die Funktion `qotd_command` auf, um das Zitat des Tages auszugeben.
    """
    await qotd_command(ctx)
#endregion

try:
    bot.run(os.environ["token"])
finally:
    if not variables.SHUTDOWN_INITIATED:
        # Protokolliert, dass der Shutdown-Prozess gestartet wird
        logging.info("Shutting down")
        # Schließt den Datenbank-Pool
        db.close_pool()
        # Schließt den Bot
        bot.close()
        # Protokolliert, dass der Shutdown-Prozess abgeschlossen ist
        logging.info("Shutdown complete")
    # Beendet das Logging
    logging.shutdown()
