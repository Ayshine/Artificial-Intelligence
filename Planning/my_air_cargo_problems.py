from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state,
)
from my_planning_graph import PlanningGraph

from functools import lru_cache


class AirCargoProblem(Problem):
    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        """

        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

    def get_actions(self):
        """
        This method creates concrete actions (no variables) for all actions in the problem
        domain action schema and turns them into complete Action objects as defined in the
        aimacode.planning module. It is computationally expensive to call this method directly;
        however, it is called in the constructor and the results cached in the `actions_list` property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        """

        # TODO create concrete Action objects based on the domain action schema for: Load, Unload, and Fly
        # concrete actions definition: specific literal action that does not include variables as with the schema
        # for example, the action schema 'Load(c, p, a)' can represent the concrete actions 'Load(C1, P1, SFO)'
        # or 'Load(C2, P2, JFK)'.  The actions for the planning problem must be concrete because the problems in
        # forward search and Planning Graphs must use Propositional Logic

        def load_actions():
            """Create all concrete Load actions and return a list

            :return: list of Action objects
            """
            loads = []
            # TODO create all load ground actions from the domain Load action
            """
            Action(Load(c, p, a),
            PRECOND: At(c, a) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
            EFFECT: ¬ At(c, a) ∧ In(c, p))
            
            Action is Load(cargo, plane, airport) so we iterate through cargos , planes and airports
            """
            for cargo in self.cargos:
                for plane in self.planes:
                    for airport in self.airports:
                        #For our preconditions above we need to check  At(c, a) and (^) At(p, a)
                       
                        precond_pos = [expr("At({}, {})".format(cargo, airport)),
                                       expr("At({}, {})".format(plane, airport))]
                        precond_neg = []

                        #After performing the action  the effect to our problem is EFFECT: ¬ At(c, a) ∧ In(c, p))
                        #some precond states should be removed (effect_rem) and some effect states should be added   

                        effect_add = [expr("In({}, {})".format(cargo, plane))]
                        effect_rem = [expr("At({}, {})".format(cargo, airport))]

                        #The load action is 
                        load = Action(expr("Load({}, {}, {})".format(cargo, plane, airport)),
                                            [precond_pos, precond_neg],
                                            [effect_add, effect_rem])
                        loads.append(load)

            return loads

        def unload_actions():
            """Create all concrete Unload actions and return a list

            :return: list of Action objects
            """
            unloads = []
            # TODO create all Unload ground actions from the domain Unload action
            """
            Action(Unload(c, p, a),
            PRECOND: In(c, p) ∧ At(p, a) ∧ Cargo(c) ∧ Plane(p) ∧ Airport(a)
            EFFECT: At(c, a) ∧ ¬ In(c, p))
            
            Action is Unload(cargo, plane, airport) so we iterate through cargos , planes and airports
            """
           
            for cargo in self.cargos:
                for plane in self.planes:
                    for airport in self.airports:

                        #For preconditions above we need to check  In(c, p) and At(p, a)                      
                        precond_pos = [expr("In({}, {})".format(cargo, plane)),
                                       expr("At({}, {})".format(plane, airport))]
                        precond_neg = []
                        

                        #EFFECT: ¬ At(c, a) ∧ In(c, p))
                        effect_add = [expr("At({}, {})".format(cargo, airport))]
                        effect_rem = [expr("In({}, {})".format(cargo, plane))]

                        #Unload action is:
                        unload = Action(expr("Unload({}, {}, {})".format(cargo, plane, airport)),
                                            [precond_pos, precond_neg],
                                            [effect_add, effect_rem])
                        unloads.append(unload)
            return unloads

        def fly_actions():
            """Create all concrete Fly actions and return a list

            :return: list of Action objects
            """
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = [expr("At({}, {})".format(p, fr)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, fr))]
                            fly = Action(expr("Fly({}, {}, {})".format(p, fr, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        """ 
        Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        #This code is used from Cake example file
        possible_actions = []
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())

        #We are going through all actions in our action list
        #But some of them cannot be perormed in the current state
        for action in self.actions_list:
            #Setting var is_possible (to be performed) to True
            is_possible = True
            #going through all positivie preconditions for current action
            for clause in action.precond_pos:
                #if that action is not in clauses (which should be) 
                #we are setting is_possible to false
                if clause not in kb.clauses:
                    is_possible = False
            #going through all negative preconditions for current action   
            for clause in action.precond_neg:
                #if that action is in clauses (which should not be) 
                #we are setting is_possible to false
                if clause in kb.clauses:
                    is_possible = False
                    
            if is_possible:
                possible_actions.append(action)

        return possible_actions

    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        # TODO implement
        new_state = FluentState([], [])
        #This code is used from Cake example file
        #The idea of this function is to define next state in our problem
        #which is going to "happen" after applying current action        
        old_state = decode_state(state, self.state_map)

        #Going through positive fluents in previous (old) state
        for fluent in old_state.pos:
            #if that fluent is not in removal_effect from action -> add it to positve fluents for new state
            if fluent not in action.effect_rem:
                new_state.pos.append(fluent)

        #going through fluents that are added by the action
        for fluent in action.effect_add:
            #if that fluent is not already in positive fluents of new state -> add it
            if fluent not in new_state.pos:
                new_state.pos.append(fluent)
        #going through negative fluents from old state
        for fluent in old_state.neg:
            #if that negative fluent is not in adding fluents of the action -> add it to negative fluents for new state
            if fluent not in action.effect_add:
                new_state.neg.append(fluent)
        #going through fluents that are being removed by the action
        for fluent in action.effect_rem:
            #if that fluent is not already in negatives for the new state -> add it
            if fluent not in new_state.neg:
                new_state.neg.append(fluent)
        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    @lru_cache(maxsize=8192)
    def h_pg_levelsum(self, node: Node):
        """This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        """
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    @lru_cache(maxsize=8192)
    def h_ignore_preconditions(self, node: Node):
        """This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        """
        # TODO implement (see Russell-Norvig Ed-3 10.2.3  or Russell-Norvig Ed-2 11.2)
        #access the logical expressions
        kb = PropKB()
        #adding positive states to propositional logic sentences
        kb.tell(decode_state(node.state, self.state_map).pos_sentence())

        #Defining counter of minimal steps to be performed to 0, which is also ideal
        #if goals found ->  count var will stay at 0
        count = 0
        
        #going through all goals in the problem
        for goal in self.goal:
            #if that goal is not alredy in positive states -> haven't reach the goal yet -> increasing counter by one
            if goal not in kb.clauses:
                count += 1
        return count


def air_cargo_p1() -> AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p2() -> AirCargoProblem:
    """  
         Problem 2 initial state and goal:
   
         Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, BOS)∧ At(P1, SFO) ∧ At(P2, JFK) ∧ At(P3, ATL)∧ Cargo(C1) ∧ Cargo(C2)
              ∧ Cargo(C3) ∧ Plane(P1) ∧ Plane(P2) ∧ Plane(P3) ∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(BOS))
         
         Goal(At(C1, JFK) ∧ At(C2, SFO) ∧ At(C3, SFO))
    """
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['ATL', 'JFK', 'SFO']
    
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(C3, ATL)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           expr('At(P3, ATL)'),
           ]
   
    neg = [expr('At(C1, ATL)'),
           expr('At(C1, JFK)'),
           expr('At(C2, ATL)'),
           expr('At(C2, SFO)'),
           expr('At(C3, JFK)'),
           expr('At(C3, SFO)'),
           expr('At(P1, ATL)'),
           expr('At(P1, JFK)'),
           expr('At(P2, ATL)'),
           expr('At(P2, SFO)'),
           expr('At(P3, JFK)'),
           expr('At(P3, SFO)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('In(C1, P3)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('In(C2, P3)'),
           expr('In(C3, P1)'),
           expr('In(C3, P2)'),
           expr('In(C3, P3)'),
           ]
    init = FluentState(pos, neg)
    
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            expr('At(C3, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p3() -> AirCargoProblem:
    """
         Problem 3 initial state and goal:

        Init(At(C1, SFO) ∧ At(C2, JFK) ∧ At(C3, ATL) ∧ At(C4, PHL)∧ At(P1, SFO) ∧ At(P2, JFK) ∧ Cargo(C1) ∧ Cargo(C2)
             ∧ Cargo(C3) ∧ Cargo(C4) ∧ Plane(P1) ∧ Plane(P2)∧ Airport(JFK) ∧ Airport(SFO) ∧ Airport(ATL) ∧ Airport(PHL))

        Goal(At(C1, JFK) ∧ At(C3, JFK) ∧ At(C2, SFO) ∧ At(C4, SFO))
    """
    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['ATL', 'JFK', 'ORD', 'SFO']
   
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(C3, ATL)'),
           expr('At(C4, ORD)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]

    neg = [expr('At(C1, ATL)'),
           expr('At(C1, JFK)'),
           expr('At(C1, ORD)'),
           expr('At(C2, ATL)'),
           expr('At(C2, ORD)'),
           expr('At(C2, SFO)'),
           expr('At(C3, JFK)'),
           expr('At(C3, ORD)'),
           expr('At(C3, SFO)'),
           expr('At(C4, ATL)'),
           expr('At(C4, JFK)'),
           expr('At(C4, SFO)'),
           expr('At(P1, ATL)'),
           expr('At(P1, JFK)'),
           expr('At(P1, ORD)'),
           expr('At(P2, ATL)'),
           expr('At(P2, ORD)'),
           expr('At(P2, SFO)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('In(C3, P1)'),
           expr('In(C3, P2)'),
           expr('In(C4, P1)'),
           expr('In(C4, P2)'),
           ]
    init = FluentState(pos, neg)
    
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            expr('At(C3, JFK)'),
            expr('At(C4, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)