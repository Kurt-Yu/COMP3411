from agent import Agent


class AI:
    def __init__(self):
        self.agent = Agent()
        self.moves = []

        self.need_axe = False
        self.need_key = False
        self.need_ss = False

    def astar(self):
        pass

    # This function is adpated from: http://inventwithpython.com/blogstatic/floodfill/recursivefloodfill.py
    # with slight modify to serve our porpuse
    # parameters: 
    #    game_map is the 2d list that represent the whole map
    #    x & y: the coordinates of starting point
    #    old_value & new_value: some character that we would like to change
    # return:
    #   Modified game_map which agent can reach from start point to anywhere else with avaliable tools
    def flood_fill(self, game_map, x, y, old_value, new_value, inventory):
        width = len(game_map)
        height = len(game_map[0])

        if old_value == None:
            old_value = game_map[x][y]

        if game_map[x][y] != old_value: # Base case. If the current x, y character is not the old_value, then do nothing.
            return

        game_map[x][y] = new_value      # Change the character at world[x][y] to newChar

        # Recursive calls. Make a recursive call as long as we are not on the
        # boundary (which would cause an Index Error.)
        if x > 0: # left
            self.flood_fill(game_map, x - 1, y, old_value, new_value, inventory)
        if y > 0: # up
            self.flood_fill(game_map, x, y - 1, old_value, new_value, inventory)
        if x < width - 1: # right
            self.flood_fill(game_map, x + 1, y, old_value, new_value, inventory)
        if y < height-1: # down
            self.flood_fill(game_map, x, y + 1, old_value, new_value, inventory)
    
    def make_action(self):
        # if we have no pending moves
        while len(self.moves) == 0:
            # if the agent already has the gold
            if self.agent.inventory['$'] > 0: 
                # use A* search to get the moves from this point to (0, 0), update self.moves
                actions = self.astar((self.agent.agent_x, self.agent.agent_y), (0, 0))  
                self.moves += actions  
            
            # if the agent found the gold
            if self.agent.is_gold_found:
                # test if agent can reach gold using the tool it has
                game_map = self.agent.convert_hashmap_to_list(self.agent.hashmap)
                copied_inventory = self.agent.inventory.copy()
                self.flood_fill(game_map, self.agent.agent_x, self.agent.agent_y, None, '#', copied_inventory)
                

                


                                
 

        