import typing as t
import datetime
import string
import traceback

import miru
import hikari

import src.development as development
import src.controller as controller

class KnightModal(miru.Modal):
    """Discord popup for playing a knight card."""

    def __init__(self, ctrl: controller.Controller, title: str, *, custom_id: t.Optional[str] = None, timeout: t.Optional[t.Union[float, int, datetime.timedelta]] = 300) -> None:
        super().__init__(title=title, custom_id=custom_id, timeout=timeout)
        self.ctrl = ctrl

    location = miru.TextInput(label="Location", placeholder="Ex: D3", required=True, custom_id="location")
    player = miru.TextInput(label="Player to rob", placeholder="Ex: Blue", required=True, custom_id="player")

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # You can also access the values using ctx.values, Modal.values, or use ctx.get_value_by_id()

        name_activator = str(ctx.author).split("#")[0].strip()
        color_robbed = str(ctx.get_value_by_id('player').strip())
        location = (list(string.ascii_uppercase).index(ctx.get_value_by_id('location')[0].upper()), float(ctx.get_value_by_id('location')[1:]))

        try:
            development.playKnight(self.ctrl, self.ctrl.get_player_by_name(name_activator), location, color_robbed)
            await ctx.respond(f"{name_activator} moved the robber to {ctx.get_value_by_id('location')} and stole from {color_robbed} with a Knight card.")
        except Exception as e:
            print(traceback.print_exc())
            await ctx.respond(content=hikari.Embed(
                title="Error!",
                description=str(e),
                color=hikari.Color(0xFF0000)))

class YOPModal(miru.Modal):
    """Discord popup for playing a year of plenty card."""

    def __init__(self, ctrl: controller.Controller, title: str, *, custom_id: t.Optional[str] = None, timeout: t.Optional[t.Union[float, int, datetime.timedelta]] = 300) -> None:
        super().__init__(title, custom_id=custom_id, timeout=timeout)
        self.ctrl = ctrl

    resource1 = miru.TextInput(label="Resource 1", placeholder="Ex: wood", required=True, custom_id="resource1")
    resource2 = miru.TextInput(label="Resource 2", placeholder="Ex: brick", required=True, custom_id="resource2")

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # You can also access the values using ctx.values, Modal.values, or use ctx.get_value_by_id()

        name = str(ctx.author).split("#")[0].strip()

        try:
            development.playYearOfPlenty(self.ctrl, self.ctrl.get_player_by_name(name), ctx.get_value_by_id('resource1'), ctx.get_value_by_id('resource2'))
            await ctx.respond(f"{str(ctx.author).split('#')[0]} recieved {ctx.get_value_by_id('resource1')} and {ctx.get_value_by_id('resource2')} from a Year of Plenty card.")
        except Exception as e:
            print(traceback.print_exc())
            await ctx.respond(content=hikari.Embed(
                title="Error!",
                description=str(e),
                color=hikari.Color(0xFF0000)))

class MonopolyModal(miru.Modal):
    """Discord popup for playing a monopoly card."""

    def __init__(self, ctrl: controller.Controller, title: str, *, custom_id: t.Optional[str] = None, timeout: t.Optional[t.Union[float, int, datetime.timedelta]] = 300) -> None:
        super().__init__(title, custom_id=custom_id, timeout=timeout)
        self.ctrl = ctrl

    resource = miru.TextInput(label="Resource to steal", placeholder="Ex: wood", required=True, custom_id="resource")

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # You can also access the values using ctx.values, Modal.values, or use ctx.get_value_by_id()

        name = str(ctx.author).split("#")[0].strip()

        try:
            development.playMonopoly(self.ctrl, self.ctrl.get_player_by_name(name), ctx.get_value_by_id('resource'))
            await ctx.respond(f"{str(ctx.author).split('#')[0]} stole all {ctx.get_value_by_id('resource')} with a Monopoly card.")
        except Exception as e:
            print(traceback.print_exc())
            await ctx.respond(content=hikari.Embed(
                title="Error!",
                description=str(e),
                color=hikari.Color(0xFF0000)))

class RoadBuildingModal(miru.Modal):
    """Discord popup for playing a road building card."""

    def __init__(self, ctrl: controller.Controller, title: str, *, custom_id: t.Optional[str] = None, timeout: t.Optional[t.Union[float, int, datetime.timedelta]] = 300) -> None:
        super().__init__(title, custom_id=custom_id, timeout=timeout)
        self.ctrl = ctrl

    road1location1 = miru.TextInput(label="Road 1 Location 1", placeholder="Ex: D3", required=True, custom_id="road1location1")
    road1location2 = miru.TextInput(label="Road 1 Location 2", placeholder="Ex: E2", required=True, custom_id="road1location2")
    road2location1 = miru.TextInput(label="Road 2 Location 1", placeholder="Ex: D3", required=True, custom_id="road2location1")
    road2location2 = miru.TextInput(label="Road 2 Location 2", placeholder="Ex: E2", required=True, custom_id="road2location2")

    # The callback function is called after the user hits 'Submit'
    async def callback(self, ctx: miru.ModalContext) -> None:
        # You can also access the values using ctx.values, Modal.values, or use ctx.get_value_by_id()

        name = str(ctx.author).split("#")[0].strip()

        loc_1_1 = (list(string.ascii_uppercase).index(ctx.get_value_by_id('road1location1')[0].upper()), int(ctx.get_value_by_id('road1location1')[1:]))
        loc_1_2 = (list(string.ascii_uppercase).index(ctx.get_value_by_id('road1location2')[0].upper()), int(ctx.get_value_by_id('road1location2')[1:]))
        loc_2_1 = (list(string.ascii_uppercase).index(ctx.get_value_by_id('road2location1')[0].upper()), int(ctx.get_value_by_id('road2location1')[1:]))
        loc_2_2 = (list(string.ascii_uppercase).index(ctx.get_value_by_id('road2location2')[0].upper()), int(ctx.get_value_by_id('road2location2')[1:]))

        road1 = (loc_1_1, loc_1_2)
        road2 = (loc_2_1, loc_2_2)

        try:
            development.playRoadBuilding(self.ctrl, self.ctrl.get_player_by_name(name), road1, road2)
            await ctx.respond(f"{str(ctx.author).split('#')[0]} built a road between {ctx.get_value_by_id('road1location1')} and {ctx.get_value_by_id('road1location2')} and a road between {ctx.get_value_by_id('road2location1')} and {ctx.get_value_by_id('road2location2')} with a Road Builder card.")
        except Exception as e:
            print(traceback.print_exc())
            await ctx.respond(content=hikari.Embed(
                title="Error!",
                description=str(e),
                color=hikari.Color(0xFF0000)))