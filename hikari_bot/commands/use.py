import lightbulb
import hikari

from hikari_bot import bot

# Plugins are structures that allow the grouping of multiple commands and listeners together.
plugin = lightbulb.Plugin("Use", description="Use a development card.")

# Creates a command in the plugin
@plugin.command
@lightbulb.option("development_card", description="Play a development card.", choices=["Knight", "Year of Plenty", "Monopoly", "Road Builder"], required=True)

@lightbulb.command("use", description="Use a development card.", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def use(ctx: lightbulb.Context) -> None:

    #TODO: Delete use messages from channel at end of each turn??

    name = str(ctx.author).split("#")[0]
    ctrl = bot.ctrl

    if ctx.options.development_card == "Knight":
        print("knight card used")
    elif ctx.options.development_card == "Year of Plenty":
            print("YEP used")
    elif ctx.options.development_card == "Monopoly":
            print("monop card used")
    else:
        print("Road Builder used")



    await bot.bot.rest.create_message(ctx.channel_id, content=hikari.Embed(
                title=f"{name} has used the {ctx.options.development_card} Card!",
                color=hikari.Color(0xFFFF00)))
    
    await ctx.respond(content="Use successful")

# Extensions are hot-reloadable (can be loaded/unloaded while the bot is live)

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)
