# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys


'''
Game plan: Use **Monte Carlo Tree Search**
1. Selection:
    Choose a starting node from the root (current position)
    Tree policy: UCT?
2. Expansion:
    Select a child (C)
3. Simulation:
    Run simulation from C til there's the end of the game (the rest of playout is random)
    Method:
        * Can we use random_agent.py to run the simulation?
4. Backpropagation:
    Update current move sequence with the result from the simulation
** Note: Value: #of tiles we earn?

How to implement tree search:
1. should we implement a class? (prob not)
2. Just work w numpy
    * Select a child step (for Selection and Expansion): create a function that list out ALL possible next moves from current move?
    * For simulation utilize random_agent.py and get results to backpropagate
    * Back propagate: "https://www.analyticsvidhya.com/blog/2019/01/monte-carlo-tree-search-introduction-algorithm-deepmind-alphago/"
        + each child has 2 values to update: t: value of simulation roll out ; n: number of times visited this node. (honestly should use a class structure for this haha)
'''

@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """

    def __init__(self):
        super(StudentAgent, self).__init__()
        self.name = "StudentAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }

    def step(self, chess_board, my_pos, adv_pos, max_step):
        """
        Implement the step function of your agent here.
        You can use the following variables to access the chess board:
        - chess_board: a numpy array of shape (x_max, y_max, 4)
        - my_pos: a tuple of (x, y)
        - adv_pos: a tuple of (x, y)
        - max_step: an integer

        You should return a tuple of ((x, y), dir),
        where (x, y) is the next position of your agent and dir is the direction of the wall
        you want to put on.

        Please check the sample implementation in agents/random_agent.py or agents/human_agent.py for more details.
        """
        # dummy return
        return my_pos, self.dir_map["u"]
