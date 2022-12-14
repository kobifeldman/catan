from typing import Union
import asyncio
import random

import hikari

import src.board as board
import src.hikari_bot.bot as bot
import src.player as player
import src.development as development
import src.hikari_bot.bot as bot
import src.longestRoad as longestRoad

class Controller:
    """Handles all tasks related to the core functionality of the game."""

    def __init__(self) -> None:
        # store deck of dev card here?
        self.player_longest_road = None
        self.player_longest_road_length = 0
        self.player_most_knights = None

        self.resource_bank = {
            "brick": 19,
            "wood": 19,
            "rock": 19,
            "wheat": 19,
            "sheep": 19
        }

        self.dev_deck = {
            "Knight":       14,
            "RoadBuilding":     2,
            "YearOfPlenty":     2,
            "Monopoly":         2,
            "VictoryPointCard": 5
        }

        self.board = None
        self.active_trades = []
        self.purchased_devs = []    # resets every turn
        self.players = []
        self.current_player = 0     # Index in self.players of the player whose turn it is
        self.flag = None
        self.cur_dice = None
        self.has_robber_moved = False
        self.cur_phase = 0      # 0 = first half of initial build cycle, 1 = 2nd half, 2 = main game, 3 = discarding
        self.victory_points_to_win = 10

    def trade(self, trade_num: int, player2: Union[player.Player, str]) -> None:
        """Handles a trade.

        Raises:
            Resource Exception: If a player does not have a resource necessary to complete the trade.
        """
        # TODO: need to add checks to verify the trade is valid: cannot give away cards, cannot trade like cards (i.e. 2 wool for 1 wool)

        # Special case: trading to the bank with a harbor
        # TODO: add this

        player1 = self.get_player_by_name(self.active_trades[trade_num - 1]["name"])
        player1_resources = self.active_trades[trade_num - 1]["p1_out"]
        player2_resources = self.active_trades[trade_num - 1]["p2_in"]

        # Need to check that all resources are available to trade before officially trading any cards
        for resource, num in player1_resources.items():
            if not player1.hasResource(resource, num):
                raise Resource(f"Player: {player1.name} does not have {num} {resource}")

        for resource, num in player2_resources.items():
            # Special case: trading to the bank
            if type(player2) is str and player2 == "bank":
                if self.resource_bank[resource] < num:
                    raise Resource(f"Bank does not have {num} {resource}")
                continue

            if not player2.hasResource(resource, num):
                raise Resource(f"Player: {player2.name} does not have {num} {resource}")

        for resource, num in player1_resources.items():
            player1.modCurrResource(resource, num * -1)
            player2.modCurrResource(resource, num)

        for resource, num in player2_resources.items():
            # Special case: trading to the bank
            if type(player2) is str and player2 == "bank":
                self.resource_bank[resource] -= num
                player1.modCurrResource(resource, num)
                continue
            
            player2.modCurrResource(resource, num * -1)
            player1.modCurrResource(resource, num)

    def build(self, player: str, building: str, location_1: tuple, location_2: Union[tuple, None]) -> Union[None, str]:
        """Maybe split this into seperate methods for each building?

        Raises:
            Resource Exception: If a player does not have a resource necessary to complete the trade.
        """
        
        player_obj = self.get_player_by_name(player)

        if building == "Road":
            if (len(player_obj.settlementSpots) > 0) and (self.cur_phase == 0 and len(player_obj.roadsPlaced) == 0) or (self.cur_phase == 1 and len(player_obj.roadsPlaced) == 1):
                if not self.board.setRoad(player_obj, location_1, location_2, self.players):
                    raise Exception("Invalid road.")
                return
            elif len(player_obj.settlementSpots) == 0:
                raise Exception("Build a settlement first.")
            elif self.cur_phase != 2:
                raise Exception("You already built your starting road for this turn.")

            if not player_obj.hasResource("wood", 1) or not player_obj.hasResource("brick", 1):
                raise Resource(f"Player: {player_obj.name} does not have the necessary resources.")

            if not self.board.setRoad(player_obj, location_1, location_2, self.players):
                raise Exception("Invalid road.")

            player_obj.modCurrResource("wood", -1)
            player_obj.modCurrResource("brick", -1)
        elif building == "Settlement":
            if (self.cur_phase == 0 and len(player_obj.settlementSpots) == 0) or (self.cur_phase == 1 and len(player_obj.settlementSpots) == 1):
                if not self.board.setSettlement(self.players, player_obj, location_1, 1):
                    raise Exception("Invalid settlement.")
                return
            elif self.cur_phase != 2:
                raise Exception("You already built your starting settlement for this turn.")

            if not player_obj.hasResource("wood", 1) or not player_obj.hasResource("brick", 1) or not player_obj.hasResource("wheat", 1) or not player_obj.hasResource("sheep", 1):
                raise Resource(f"Player: {player_obj.name} does not have the necessary resources.")

            if not self.board.setSettlement(self.players, player_obj, location_1, 1):
                raise Exception("Invalid settlement.")

            player_obj.modCurrResource("wood", -1)
            player_obj.modCurrResource("brick", -1)
            player_obj.modCurrResource("wheat", -1)
            player_obj.modCurrResource("sheep", -1)
        elif building == "City":
            if not player_obj.hasResource("wheat", 2) or not player_obj.hasResource("rock", 3):
                raise Resource(f"Player: {player_obj.name} does not have the necessary resources.")

            if not self.board.setSettlement(self.players, player_obj, location_1, 2):
                raise Exception("Invalid city.")

            player_obj.modCurrResource("wheat", -2)
            player_obj.modCurrResource("rock", -3)
        elif building == "Development Card":
            if not player_obj.hasResource("wheat", 1) or not player_obj.hasResource("rock", 1) or not player_obj.hasResource("sheep", 1):
                raise Resource(f"Player: {player_obj.name} does not have the necessary resources.")

            bought_card = development.buyDevCard(player_obj, self.dev_deck)
            self.purchased_devs.append(bought_card)

            if bought_card == "VictoryPointCard":
                development.playVictoryPointCard(player_obj)

            player_obj.modCurrResource("wheat", -1)
            player_obj.modCurrResource("rock", -1)
            player_obj.modCurrResource("sheep", -1)

            return bought_card

    def move_robber(self, new_location: tuple, player_to_rob: str) -> str:
        """Moves the robber."""

        # verify there is at least 1 player that can be stolen from
        atleast_1 = False
        for player in self.players:
            if player.name != player_to_rob:
                for num in player.currentResources.values():
                    if num > 0:
                        atleast_1 = True
                        break
            if atleast_1: break
        
        player_to_rob = self.get_player_by_color(player_to_rob)
        self.board.moveRobber(new_location)
        stolenCard = None

        if not atleast_1:
            return

        for tile in self.board.settleOnTile:
            if '(' + str(self.board.robberLocation[0]) + ',' + str(self.board.robberLocation[1]) + ')' in tile:
                if player_to_rob.name + "'s Settlement" or player_to_rob.name + "'s City" in self.board.settleOnTile[tile]:
                    possibleStolenCards = []
                    for card in player_to_rob.currentResources:
                        if player_to_rob.currentResources[card] > 0:
                            possibleStolenCards.append(card)
                    
                    if(len(possibleStolenCards) == 0):
                        raise Exception(f"{player_to_rob} does not have any cards to steal.")

                    stolenCard = random.choice(possibleStolenCards)

                    player_to_rob.currentResources[stolenCard] -= 1
                    self.players[self.current_player].currentResources[stolenCard] += 1

        return stolenCard

    def has_won(self) -> Union[None, player.Player]:
        """Checks if any players have won the game."""

        for player in self.players:
            if player.victoryPoints >= self.victory_points_to_win:
                return player

        return None

    def largest_army(self):

        for player in self.players:
            if player.usedDevelopmentCards["Knight"] >= 3 and (self.player_most_knights is None or self.player_most_knights.usedDevelopmentCards["Knight"] < player.usedDevelopmentCards["Knight"]):
                if self.player_most_knights is not None:
                    self.player_most_knights.largestArmy = False
                    self.player_most_knights.victoryPoints -= 2

                player.largestArmy = True
                player.victoryPoints += 2

                self.player_most_knights = player

        if self.player_most_knights is None:
            return


    def longest_road(self):
        for player in self.players:
            curPlayerLongestRoad = longestRoad.outerLongestRoad(player.roadsPlaced, self.players, player)
            if curPlayerLongestRoad >= 5 and (self.player_longest_road is None or self.player_longest_road_length < curPlayerLongestRoad):

                self.player_longest_road_length = curPlayerLongestRoad

                if self.player_longest_road is not None:
                    self.player_longest_road.longestRoad = False
                    self.player_longest_road.victoryPoints -= 2

                player.longestRoad = True
                player.victoryPoints += 2

                self.player_longest_road = player

        if self.player_longest_road is None:
            return


    def roll_dice(self) -> int:
        """Rolls 2 dice randomly."""

        return random.randint(1, 6) + random.randint(1, 6)

    def get_player_by_name(self, name: str) -> player.Player:
        """Returns the player object given a name OR raises an error if none found."""

        for p in self.players:
            if p.name == name:
                return p

        raise Exception("Player not found!")

    def get_player_by_color(self, color: str) -> player.Player:
        """Returns the player object given a color OR raises an error if none found."""

        for p in self.players:
            if p.color == color:
                return p

        raise Exception("Player not found!")

    def add_player(self, name: str, color: str) -> None:
        """Adds a new player to the game."""

        p = player.Player(name, color)
        self.players.append(p)

def setup() -> Controller:
    """Handles all game setup."""
 
    # players are given a color, and their starting pieces
    # via some method, board is setup
    # players are randomly given a starting order (or with dice rolls)
    # put the first 2 settling turns in here or main loop?

    ctrl = Controller()

    return ctrl

async def run(ctrl: Controller, flag: asyncio.Event, drawing_mode: str) -> None:
    """Controls the main game loop."""
    # upon every relevent action, checking if the player has won needs to happen: building city/settlement/development card or recieving largest army/longest road

    ctrl.board = board.Board(drawing_mode)
    winner = None

    ctrl.flag = flag

    random.shuffle(ctrl.players)

    # Handle initial settlement and road placements
    for i, player in enumerate(ctrl.players):
        ctrl.current_player = i

        await bot.send_image_or_message(None, f"{player.name}'s turn to build a settlement and road.\nUse /build")
        await bot.send_image_or_message("images/test.png", None)

        await ctrl.flag.wait()

        ctrl.flag.clear()

    ctrl.cur_phase = 1
    ctrl.players.reverse()

    for i, player in enumerate(ctrl.players):
        ctrl.current_player = i

        await bot.send_image_or_message(None, f"{player.name}'s turn to build a settlement and road.\nUse /build")
        await bot.send_image_or_message("images/test.png", None)

        await ctrl.flag.wait()

        ctrl.flag.clear()

    ctrl.players.reverse()
    ctrl.cur_phase = 2

    random.shuffle(ctrl.players)

    while winner is None:
        ctrl.has_robber_moved = False
        ctrl.flag.clear()
        ctrl.active_trades.clear()     # emptied at start of each turn
        ctrl.purchased_devs.clear()     # emptied at start of each turn

        ctrl.cur_dice = ctrl.roll_dice()
        message = hikari.Embed(title=f"{ctrl.players[ctrl.current_player].name}'s turn",
                description=f"Dice roll: {ctrl.cur_dice}",
                color=hikari.Color(0x00FF00)
        )
        await bot.send_image_or_message(None, message)

        await bot.send_image_or_message("images/test.png", None)
        
        if ctrl.cur_dice == 7:
            # Prompt player's with more than 7 cards to discard half
            players_over_7 = []

            for player in ctrl.players:
                sum = 0

                for val in player.currentResources.values():
                    sum += val

                if sum > 7:
                    players_over_7.append(player.name)
                    player.cardsToDiscard = sum // 2

            if len(players_over_7) > 0:
                await bot.send_image_or_message(None, f"Players with over 7 cards: {*players_over_7,}")     # "*" used to unpack the list
                await bot.send_image_or_message(None, "Use /discard <cards> to get rid of half of your cards.")

                ctrl.cur_phase = 3
                await ctrl.flag.wait()
                ctrl.flag.clear()
                ctrl.cur_phase = 2

            # Prompt player for new robber location, wait for response
            await bot.send_image_or_message(None, "Use /rob <location> <player> to move the robber and steal from someone.")

            await ctrl.flag.wait()
            ctrl.flag.clear()
            ctrl.has_robber_moved = True
        else:
            ctrl.board.getMaterial(ctrl.players, ctrl.cur_dice)  # give all players their materials based on the roll of the dice

        await ctrl.flag.wait()  # flag is set when play calls the /endturn command

        # Update current player
        if ctrl.current_player == len(ctrl.players) - 1:
            ctrl.current_player = 0
        else:
            ctrl.current_player += 1

        ctrl.largest_army()
        ctrl.longest_road()

        winner = ctrl.has_won()

    await game_over(winner)

async def game_over(winner: player.Player) -> None:
    """Handles any cleanup that needs to occur when a player wins the game."""
    
    message = hikari.Embed(title=f"Congratulations!",
                description=f"{winner.name} has won the game",
                color=hikari.Color(0x00FF00)
        )
    await bot.send_image_or_message(None, message)

class Resource(Exception):
    """Custom exception representing when a player does not have a resource."""
    pass

class RobberException(Exception):
    """Custom exception representing when no players have any resources that can be stolen."""
    pass