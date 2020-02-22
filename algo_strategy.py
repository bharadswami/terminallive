import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips:

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical
  board states. Though, we recommended making a copy of the map to preserve
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER, BITS, CORES
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        BITS = 1
        CORES = 0
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.cores_to_keep = 0.5
        self.custom_layout = [[(FILTER,0,2), (FILTER,0,2), None, None, None, None, None, None, None, None, None, None, None, (FILTER,3,5), None, (FILTER,3,5), None, None, None, None, None, None, None, None, None, None, (FILTER,0,2), (FILTER,0,2)], [None, (DESTRUCTOR,1,-1), (FILTER,0,6), None, None, None, None, None, None, None, None, None, None, (FILTER,3,5), None, (FILTER,3,5), None, None, None, None, None, None, None, None, None, (FILTER,0,17), (DESTRUCTOR,1,-1), None], [None, None, (FILTER,16,-1), (FILTER,0,6), (FILTER,0,6), None, None, None, None, None, None, None, None, (FILTER,3,18), None, (FILTER,3,18), None, None, None, None, None, None, None, None, None, (FILTER,0,17), None, None], [None, None, None, (ENCRYPTOR,8,9), (ENCRYPTOR,6,7), (FILTER,0,6), None, None, None, None, None, None, None, (FILTER,3,18), None, (FILTER,3,18), None, None, None, None, None, None, None, None, (FILTER,0,17), None, None, None], [None, None, None, None, (ENCRYPTOR,4,5), (FILTER,0,6), None, None, None, None, None, None, None, (FILTER,3,18), None, (FILTER,3,18), None, None, None, None, None, None, None, (FILTER,0,17), None, None, None, None], [None, None, None, None, None, (ENCRYPTOR,10,11), None, (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,2), None, (FILTER,0,2), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), (FILTER,0,17), None, None, None, None, None], [None, None, None, None, None, None, None, None, (ENCRYPTOR,12,13), (ENCRYPTOR,14,15), None, None, None, (DESTRUCTOR,1,-1), None, (DESTRUCTOR,1,-1), None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]
        self.default_reqs = self.layout_to_request_list(self.custom_layout)

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        self.custom_strategy(game_state)

        game_state.submit_turn()

    def custom_strategy(self, game_state):
        """Master method"""
        self.complete_requests(game_state, self.default_reqs)


# Helpers
    def layout_to_request_list(self, layout):
        """
        LAYOUT: 2D array representing the game map. Vaules in the array are:
             a) None: if we want this to be empty or
             b) (UNIT_TYPE, UNIT_PRIORITY, UPGRADE_PRIORITY)

        Returns REQUEST_LIST: (SPAWN/UPGRADE, UNIT_TYPE, LOCATION, PRIORITY) sorted by priority
            - SPAWN/UPGRADE: 0 for spawn requests, 1 for upgrade requests
            - UNIT_TYPE: type of unit
            - LOCATION: tuple of location
            - PRIORITY: Priority of request
        """
        request_list = []
        for i in range(len(layout)):
            for j in range(len(layout[0])):
                if layout[i][j]:
                    gamelib.debug_write(i, j, layout[i][j])
                    spawn_req = (0, layout[i][j][0], [i, j], layout[i][j][1])
                    request_list.append(spawn_req)
                    if layout[i][j][2] != -1:
                        upgrade_req = (1, layout[i][j][0], [i, j], layout[i][j][2])
                        request_list.append(upgrade_req)

        request_list.sort(key=lambda req: req[3])
        return request_list

    def complete_requests(self, game_state, request_list, max_priority = math.inf):
        for request in request_list:
            if (game_state.get_resource(1) < self.cores_to_keep) or (request[3] > max_priority):
                return
            if request[0] == 0:
                if game_state.can_spawn(request[1], request[2]):
                    game_state.attempt_spawn(request[1], request[2])
            elif request[0] == 1:
                game_state.attempt_upgrade(request[2])

# Possibly useful helper methods from starter algo
    def least_damage_spawn_location(self, game_state, location_options):
        """
        This function will help us guess which location is the safest to spawn moving units from.
        It gets the path the unit will take then checks locations on that path to
        estimate the path's damage risk.
        """
        damages = []
        # Get the damage estimate each path will take
        for location in location_options:
            path = game_state.find_path_to_edge(location)
            damage = 0
            for path_location in path:
                # Get number of enemy destructors that can attack the final location and multiply by destructor damage
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage_i
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))

    def simulate_path(self, game_state, start_location, unit, count):
        unit = gamelib.GameUnit(unit, game_state.config)
        path = game_state.find_path_to_edge(start)
        wall_poped = 0
        destroyer_damaged = 0
        breaches = 0
        damage_done = 0
        health = unit.max_health
        destroyed_list = []

        if path[len(path) - 1] in game_state.game_map.get_edges()[0] or path[len(path) - 1] in game_state.game_map.get_edges()[1]:
            frame = 0
            i = 0
            while (i < len(path)):
                if count == 0 :
                    break
                location = path[i]
                for _ in range(count):
                    target = game_state.get_target(unit, location)
                    if target: 
                        if target.health <= unit.damage_f:
                            if target.unit_type == FILTER:
                                wall_poped += 1
                            destroyed_list.append(target)
                            if target.unit_type == DESTRUCTOR:
                                destroyer_damaged += target.health
                            damage_done += target.health
                        else :
                            target.health -= unit.damage_f
                            if target.unit_type == DESTRUCTOR:
                                destroyer_damaged += unit.damage_f
                            damage_done += unit.damage_f
                for attacker in game_state.get_attackers(location, 0):
                    if attacker not in destroyed_list:
                        health -= attacker.damage_i
                        if health <= 0:
                            count -= 1
                            health = unit.max_health
                if frame == unit.speed:
                    i += 1
                    frame = -1
                frame += 1
            if i == len(path):
                breaches += count
            return damage_done, wall_poped, destroyer_damaged, breaches
        return 0,0,0,-1


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
