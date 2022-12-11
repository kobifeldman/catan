import lightbulb
import hikari

import src.hikari_bot.bot as bot

# Plugins are structures that allow the grouping of multiple commands and listeners together.
plugin = lightbulb.Plugin("Discard", description="Discard resource cards.")

# Creates a command in the plugin
@plugin.command
@lightbulb.option("brick", description="Brick cards to discard", required=True, default=0, type=int)
@lightbulb.option("wood", description="Wood cards to discard", required=True, default=0, type=int)
@lightbulb.option("rock", description="Rock cards to discard", required=True, default=0, type=int)
@lightbulb.option("wheat", description="Wheat cards to discard", required=True, default=0, type=int)
@lightbulb.option("sheep", description="Sheep cards to discard", required=True, default=0, type=int)
@lightbulb.command("discard", description="Discard resource cards.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def discard(ctx: lightbulb.Context) -> None:
    name = str(ctx.author).split("#")[0]
    ctrl = bot.ctrl

    cards_to_dict = {
        "brick": int(ctx.options.brick),
        "wood": int(ctx.options.wood),
        "rock": int(ctx.options.rock),
        "wheat": int(ctx.options.wheat),
        "sheep": int(ctx.options.sheep)
    }
    total = sum(cards_to_dict.values())
    
    # prevent player from discarding incorrect # of cards
    if total != ctrl.get_player(name).cardsToDiscard:
        await ctx.respond(content=hikari.Embed(
                title="Error!",
                description=f"You need to discard {ctrl.get_player(name).cardsToDiscard} cards.",
                color=hikari.Color(0xFF0000)))

        return

    # prevent discarding negative cards and cards you don't have
    for card, val in cards_to_dict.items():
        if val < 0:
            await ctx.respond(content=hikari.Embed(
                title="Error!",
                description=f"You cannot discard negative cards.",
                color=hikari.Color(0xFF0000)))

            return

        if ctrl.get_player(name).currentResources[card] < val:
            await ctx.respond(content=hikari.Embed(
                title="Error!",
                description=f"You do not have {val} {card} cards to discard.",
                color=hikari.Color(0xFF0000)))

            return

    for card, val in cards_to_dict.items():
        ctrl.resource_bank[card] += val
        ctrl.get_player(name).currentResources[card] -= val

    ctrl.get_player(name).cardsToDiscard = 0

    await ctx.respond(content=f"Successfully discarded {total} cards.")

    all_discarded = True
    for player in ctrl.players:
        if player.cardsToDiscard > 0:
            all_discarded = False
            break

    if all_discarded:
        ctrl.flag.set()

# Extensions are hot-reloadable (can be loaded/unloaded while the bot is live)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)