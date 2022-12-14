import lightbulb
import hikari

import src.controller as controller
import src.hikari_bot.bot as bot

# Plugins are structures that allow the grouping of multiple commands and listeners together.
plugin = lightbulb.Plugin("Accept", description="Accept a trade.")

# Creates a command in the plugin
@plugin.command
@lightbulb.option("trade_num", description="# of the trade to accept.", type=int, required=True)
@lightbulb.command("accept", description="Accept a trade.")
@lightbulb.implements(lightbulb.SlashCommand)
async def accept(ctx: lightbulb.Context) -> None:
    """Accept a trade.

    Called via the discord command '/accept <trade number>.
    The player whose turn it is can accept any trade OR any player can accept a trade from the player whose turn it is.
    """

    active_trades = bot.ctrl.active_trades
    player1_name = active_trades[ctx.options.trade_num - 1]["name"]
    player2_name = str(ctx.author).split("#")[0]

    # Cannot accept your own trade
    if player1_name == player2_name:
        await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, content=hikari.Embed(
                title="Error!",
                description=f"You cannot accept your own trade.",
                color=hikari.Color(0xFF0000)))
        return

    # Player whose turn it is must be one of the player's involved in the trade
    if player1_name != bot.ctrl.players[bot.ctrl.current_player].name and player2_name != bot.ctrl.players[bot.ctrl.current_player].name:
        await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, content=hikari.Embed(
                title="Error!",
                description=f"Player {bot.ctrl.players[bot.ctrl.current_player]} must be involved in the trade.",
                color=hikari.Color(0xFF0000)))
        return

    # Invalid trade offer to accept
    if ctx.options.trade_num > len(bot.ctrl.active_trades):
        await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, content=hikari.Embed(
                title="Error!",
                description=f"Trade Offer #: {ctx.options.trade_num} is invalid.",
                color=hikari.Color(0xFF0000)))
        return

    try:
        bot.ctrl.trade(ctx.options.trade_num, bot.ctrl.get_player_by_name(player2_name))

        await ctx.respond(content=f"Trade # {ctx.options.trade_num} from {player1_name} accepted by {player2_name}.")
    except controller.Resource:
        await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, content=hikari.Embed(
                title="Error!",
                description=f"A player does not have the necessary resources to complete the trade.",
                color=hikari.Color(0xFF0000)))
    except Exception as e:
        await ctx.respond(flags=hikari.MessageFlag.EPHEMERAL, content=hikari.Embed(
                title="Error!",
                description=f"Failed to do the trade: {e}",
                color=hikari.Color(0xFF0000)))
    

# Extensions are hot-reloadable (can be loaded/unloaded while the bot is live)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)