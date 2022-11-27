# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
"""These imports under needs to be deleted later"""
import logging

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
1. should we implement a class? 
2. Just work w numpy
    * Select a child step (for Selection and Expansion): create a function that list out ALL possible next moves from current move?
    * For simulation utilize random_agent.py and get results to backpropagate
    * Back propagate: "https://www.analyticsvidhya.com/blog/2019/01/monte-carlo-tree-search-introduction-algorithm-deepmind-alphago/"
        + each child has 2 values to update: t: value of simulation roll out ; n: number of times visited this node. (honestly should use a class structure for this haha)
'''
logger=logging.getLogger(__name__)
@register_agent("student_agent")
class StudentAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """
    class MCnodes: # check https://github.com/hayoung-kim/mcts-tic-tac-toe/blob/master/VanilaMCTS.py
            def __init__(self,my_pos,barrier_dir,adv_pos,root=None,value=0,n=0,chess_board=None,visited=0):
                """
                Initialize the nodes for Monte Carlo Tree Search
                """
                # logger.info(f"Initializing node {move}")
                self.barrier_dir=barrier_dir
                self.value=value
                self.n=n
                self.chess_board=chess_board
                self.my_pos=my_pos
                self.adv_pos=adv_pos
                self.moves=((-1, 0), (0, 1), (1, 0), (0, -1))
                self.children=[]
                self.visited=visited
                # if tree==None:
                #     self.tree=self.create_tree()

            def is_valid_child(self,move): #taken from world.py file
                print("checking ",move)
                (r,c),d=move
                if self.chess_board[r, c, d]:
                    return False
                if (self.my_pos==(r,c)):
                    return True
                pos=(r,c)
                # Get position of the adversary
                adv_pos = self.adv_pos

                # BFS
                state_queue = [(self.my_pos, 0)]
                visited = {tuple(self.my_pos)}
                is_reached = False
                M=len(self.chess_board) #chess board size
                k=(M+1)//2 #K as defined in the pdf
                while state_queue and not is_reached:
                    cur_pos, cur_step = state_queue.pop(0)
                    r, c = cur_pos
                    if cur_step == k:
                        break
                    for dir, m in enumerate(self.moves):
                        if self.chess_board[r, c, dir]:
                            continue

                        next_pos = (cur_pos[0] + m[0],cur_pos[1]+m[1])
                        if (pos==adv_pos) or tuple(next_pos) in visited:
                            
                            continue
                        if (pos==next_pos):
                            is_reached = True
                            break

                        visited.add(tuple(next_pos))
                        state_queue.append((next_pos, cur_step + 1))
                return is_reached


            def get_children(self):
                """
                Generate possible children nodes (valid moves) from a node
                From deduction, for k max steps, the "reachable" region of a node is (ignoring boundary of board) a diamnod shaped bounding with vertices k-step away from the node
                """
                children=[]
                # logger.info(f"Generate children for {self.move}")
                M=len(self.chess_board) #chess board size
                k=(M+1)//2 #K as defined in the pdf
                moves=[] 
                #generate possible moves
                for i in range(k+1):
                    for j in range (k-i+1):
                        if (i,j)==(0,0): #can't not move
                            continue
                        moves.extend([(i,j),(-i,j),(i,-j),(-i,-j)])
                for m in moves:
                    r=self.my_pos[0]+m[0]
                    c=self.my_pos[1]+m[1]
                    if r<0 or c<0 or r>=M or c>=M:
                        continue
                    m=(r,c)
                    for d in [0,1,2,3]:
                        if (m,d) in children:
                            continue
                        if self.is_valid_child((m,d)):
                            children.append((m,d))
                for c in children:
                    m,d=c
                    child=MCnodes(m,d,self.adv_pos,root=self,chess_board=self.chess_board)
                    self.children.append(child)
                return None
            
            def selection(self):
                """
                Perform selection based on UCT Q*(s,a)=Q(s,a)+2*sqrt(log(n(s))/n(s,a))
                """
                max_child=self.children[0]
                if max_child.visited==0:
                    max_uct=max_child.value+4*math.sqrt(math.log(1)/1e-100)
                else:
                    max_uct=max_child.value+4*math.sqrt(math.log(1)/max_child.visited)
                for c in self.children:
                    if c.visited ==0:
                        c_uct=c.value+4*math.sqrt(math.log(1)/0.000001)
                    else:
                        c_uct=c.value+4*math.sqrt(math.log(1)/0.0000001)


                    print(c_uct,c.my_pos,c.barrier_dir)
                    if c_uct>max_uct:
                        max_uct=c_uct
                        max_child=c
                return max_child


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
