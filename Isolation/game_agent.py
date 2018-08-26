"""Finish all TODO items in this file to complete the isolation project, then
test your agent's strength against a set of known agents using tournament.py
and include the results in your report.
"""
class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    This should be the best heuristic function for your project submission.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of thse
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    # TODO: finish this function!
    if game.is_loser(player):
        return float('-inf')

    if game.is_winner(player):
        return float('inf')

#######################################
    player_moves = len(game.get_legal_moves(player))
    opponent_moves = len(game.get_legal_moves(game.get_opponent(player)))

    # Corners limit directions a player can move. Then,
    # Penalize player for moving to corner positions.
    corner_weight = 2
    if is_curr_location_corner(game, game.get_player_location(player)):
        player_moves -= corner_weight

    return float(player_moves - opponent_moves)



def is_curr_location_corner(game, player_location):
    """Return true if player current location is on a board corner"""
    corner_positions = [(0, 0), (0, game.height - 1), (game.width - 1, 0), (game.width - 1, game.height - 1)]
    return player_location in corner_positions
   

def custom_score_2(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """

    # TODO: finish this function!
    if game.is_loser(player):
        return float('-inf')

    if game.is_winner(player):
        return float('inf')
    # get player legal moves
    player_legal_moves = len(game.get_legal_moves(player))
    # Get the total number of Moves available for the Opponent
    opponent_legal_moves = len(game.get_legal_moves(game.get_opponent(player)))

    # Initial Calculaton is based on the difference between the # of moves between the agent and the player
    calculated_score = player_legal_moves - opponent_legal_moves

    # Penalty determination depending on stage of game
    start_game_penalty = .1
    mid_game_penalty = .4
    near_end_game_penalty = .7
    end_game_penalty = .9

    total_available_space = game.width * game.height
    current_state_of_game = len(game.get_blank_spaces())
    game_level = current_state_of_game/total_available_space

    # Initial Penalty
    penalty = 0

    # Assigning Penalties depending on game stage
    if game_level <=.25:
        penalty = start_game_penalty

    elif game_level  > .25 and game_level <= .4:
        penalty = mid_game_penalty

    elif game_level > .4 and game_level <= .7:
        penalty = near_end_game_penalty

    elif game_level > .7:
        penalty = end_game_penalty

    # Getting current position of the agent and the opponent
    player_position = game.get_player_location(player)
    opponent_position = game.get_player_location(game.get_opponent(player))

    # Corner coordinates
    corners = [(0,0), (0,(game.width -1)), (game.height-1,0), ((game.height-1), (game.width-1))]

    #Let's try more sophisticated heuristic
    # Rewarding or Penalizing Scores for occupying corner positions
    if player_position in corners:
        calculated_score = calculated_score - (2*penalty * calculated_score)
    if opponent_position in corners:
        calculated_score = calculated_score + (2*penalty * calculated_score)

    return float(calculated_score)
  
    

def custom_score_3(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    Note: this function should be called from within a Player instance as
    `self.score()` -- you should not need to call this function directly.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    # TODO: finish this function!
    if game.is_loser(player):
        return float('-inf')

    if game.is_winner(player):
        return float('inf')
     # Let's try a simple heuristic
     # Player has moves to play. How many more than the opponent?
    player_moves_left = len(game.get_legal_moves(player))
    opponent_moves_left = len(game.get_legal_moves(game.get_opponent(player)))
    return float(player_moves_left - opponent_moves_left)
    

class IsolationPlayer:
    """Base class for minimax and alphabeta agents -- this class is never
    constructed or tested directly.

    ********************  DO NOT MODIFY THIS CLASS  ********************

    Parameters
    ----------
    search_depth : int (optional)
        A strictly positive integer (i.e., 1, 2, 3,...) for the number of
        layers in the game tree to explore for fixed-depth search. (i.e., a
        depth of one (1) would only explore the immediate sucessors of the
        current state.)

    score_fn : callable (optional)
        A function to use for heuristic evaluation of game states.

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted. Should be a
        positive value large enough to allow the function to return before the
        timer expires.
    """
    def __init__(self, search_depth=3, score_fn=custom_score, timeout=10.):
        self.search_depth = search_depth
        self.score = score_fn
        self.time_left = None
        self.TIMER_THRESHOLD = timeout


class MinimaxPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using depth-limited minimax
    search. You must finish and test this player to make sure it properly uses
    minimax to return a good move before the search time limit expires.
    """
        
    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **************  YOU DO NOT NEED TO MODIFY THIS FUNCTION  *************

        For fixed-depth search, this function simply wraps the call to the
        minimax method, but this method provides a common interface for all
        Isolation agents, and you will replace it in the AlphaBetaPlayer with
        iterative deepening search.

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        # Initialize the best move so that this function returns something
        # in case the search fails due to timeout
        best_move = (-1, -1)

        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.
            return self.minimax(game, self.search_depth)

        except SearchTimeout:
            pass  # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def minimax(self, game, depth):
        """Implement depth-limited minimax search algorithm as described in
        the lectures.

        This should be a modified version of MINIMAX-DECISION in the AIMA text.
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Minimax-Decision.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        # TODO: finish this function!       
         # Note: No need to return move, as the max/min players keep track of them
        if depth == 0:           
            return (self.score(game, self), None)

        # Verify if there are any available legal moves
        
        best_move = None
        best_score = float('-inf')
      
#        if not legal_moves:
#            return (game.utility(self), (-1, -1))
       
        
        for move in game.get_legal_moves():
            score = self.minimax_min(game.forecast_move(move), depth-1)
            if score > best_score:
                best_score = score
                best_move = move     
     
        return best_move

    def minimax_max(self, game, depth):
        """Minimax maximizer player. Returns the highest score found in game
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        if depth == 0:
            return self.score(game, self)
        
        value = float('-inf')
         
        for move in game.get_legal_moves():
            value  = max(value,self.minimax_min(game.forecast_move(move), depth - 1))
            
        return value

    def minimax_min(self, game, depth):
        """Minimax minimizer player. Returns the lowest score found in game
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
        if depth == 0:
            return self.score(game, self)
        
        value = float('inf')
        
        for move in game.get_legal_moves():
            
            value = min(value , self.minimax_max(game.forecast_move(move), depth - 1))

        return value

class AlphaBetaPlayer(IsolationPlayer):
    """Game-playing agent that chooses a move using iterative deepening minimax
    search with alpha-beta pruning. You must finish and test this player to
    make sure it returns a good move before the search time limit expires.
    """
        
    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        Modify the get_move() method from the MinimaxPlayer class to implement
        iterative deepening search instead of fixed-depth search.

        **********************************************************************
        NOTE: If time_left() < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left
        # TODO: finish this function!
     
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
        
#        legal_moves = game.get_legal_moves()
#        if not legal_moves:
#            return (-1,-1)
            
        best_move = (-1, -1)
        try:
            # The try/except block will automatically catch the exception
            # raised when the timer is about to expire.

            iterative_depth = 1
            while True:
               best_move = self.alphabeta(game, iterative_depth)
               iterative_depth += 1

        except SearchTimeout:
            pass

        return best_move        

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """Implement depth-limited minimax search with alpha-beta pruning as
        described in the lectures.

        This should be a modified version of ALPHA-BETA-SEARCH in the AIMA text
        https://github.com/aimacode/aima-pseudocode/blob/master/md/Alpha-Beta-Search.md

        **********************************************************************
            You MAY add additional methods to this class, or define helper
                 functions to implement the required functionality.
        **********************************************************************

        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves

        Notes
        -----
            (1) You MUST use the `self.score()` method for board evaluation
                to pass the project tests; you cannot call any other evaluation
                function directly.

            (2) If you use any helper functions (e.g., as shown in the AIMA
                pseudocode) then you must copy the timer check into the top of
                each helper function or else your agent will timeout during
                testing.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()
            

        game_over = (-1, -1)

        best_score = float("-inf")
       
        if not game.get_legal_moves():
           return game_over

        best_move = game.get_legal_moves()[0]
        
        for move in game.get_legal_moves():
             
            val = self.min_value(game.forecast_move(move), depth-1, alpha, beta)
            if val > best_score:
                best_score = val
                best_move = move
            alpha = max(val, alpha) 
            
        return best_move
           
    
    def min_value(self, game, depth, alpha, beta):
        """ Return the value for a win (+1) if the game is over,
        otherwise return the minimum value over all legal child
        nodes.
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        if depth == 0:
           return self.score(game, self)

        if not game.get_legal_moves():
           return self.score(game, self)



        value = float("inf")
        for move in game.get_legal_moves():
            value = min(value, self.max_value(game.forecast_move(move), depth - 1, alpha, beta))
       # check current value lesser than than the maximum bound alpha in the maximizer function a level up
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value



    def max_value(self, game, depth, alpha, beta):
        """ Return the value for a loss (-1) if the game is over,
        otherwise return the maximum value over all legal child
        nodes.
        """

        if self.time_left() < self.TIMER_THRESHOLD:
           raise SearchTimeout()

        if depth == 0:
           return self.score(game, self)
    
        if not game.get_legal_moves():
           return self.score(game, self)


        value = float("-inf")
        for move in game.get_legal_moves():
            value = max(value, self.min_value(game.forecast_move(move), depth - 1, alpha, beta))
       # check current value lesser than than the maximum bound alpha in the maximizer function a level up
            if value >= beta:
               return value
            alpha = max(alpha, value)
        return value