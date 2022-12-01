# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent

import math,copy
"""These imports under needs to be deleted later"""

"""
NEW game plan: Chasing algorithm (https://www.rebellionresearch.com/what-is-monte-carlo-tree-search-used-for )
* find best children (closest to the oponent)
    Choose a starting node from the root (current position)
* grade them : 
    heuristics: closer to center
                barrier towards oponent
* if any of them make us win -> auto choose
                 make us loose -> yeet
"""




@register_agent("student_agent")
class StudentAgent(Agent):
    
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """
    class Node: # check https://github.com/hayoung-kim/mcts-tic-tac-toe/blob/master/VanilaMCTS.py
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
            self.opposites={0: 2, 1: 3, 2: 0, 3: 1}
            self.children=[]
            self.visited=visited
            # if tree==None:
            #     self.tree=self.create_tree()
        def __lt__(self, other):
            return self.value < other.value

        def is_valid_child(self,move): #taken from world.py file
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
            
            def set_barrier(board,pos, dir):
                r,c=pos
                # Set the barrier to True
                board[r, c, dir] = True
                # Set the opposite barrier to True
                moves=((-1, 0), (0, 1), (1, 0), (0, -1))
                opposites={0: 2, 1: 3, 2: 0, 3: 1}
                move = moves[dir]
                board[r + move[0], c + move[1], opposites[dir]] = True
                return board
            children=[]
            # logger.info(f"Generate children for {self.move}")
            M=len(self.chess_board) #chess board size
            k=(M+1)//2 #K as defined in the pdf
            ms=[] 
            #generate possible moves
            for i in range(k+1):
                for j in range (k-i+1):
                    if (i,j)==(0,0): #can't not move
                        continue
                    ms.extend([(i,j),(-i,j),(i,-j),(-i,-j)])
            for m in ms:
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
                board=copy.deepcopy(self.chess_board)
                m,d=c
                child=StudentAgent.Node(m,d,self.adv_pos,root=self,chess_board=set_barrier(board,m,d))
                self.children.append(child)
            return None
            
        
        # def selection(self):
        #     """
        #     Perform selection based on UCT Q*(s,a)=Q(s,a)+2*sqrt(log(n(s))/n(s,a))
        #     """
        #     max_child=self.children[0]
        #     if max_child.visited==0:
        #         max_uct=max_child.value+4*math.sqrt(math.log(1)/1e-100)
        #     else:
        #         max_uct=max_child.value+4*math.sqrt(math.log(1)/max_child.visited)
        #     for c in self.children:
        #         if c.visited ==0:
        #             c_uct=c.value+4*math.sqrt(math.log(1)/0.000001)
        #         else:
        #             c_uct=c.value+4*math.sqrt(math.log(1)/0.0000001)


        #         print(c_uct,c.my_pos,c.barrier_dir)
        #         if c_uct>max_uct:
        #             max_uct=c_uct
        #             max_child=c
        #     return max_child
        def check_endgame(self):
            """
            Check if the game ends and compute the current score of the agents.

            Returns
            -------
            is_endgame : bool
                Whether the game ends.
            player_1_score : int
                The score of player 1.
            player_2_score : int
                The score of player 2.
            """
            # Union-Find
            board_size=len(self.chess_board)
            father = dict()
            for r in range(board_size):
                for c in range(board_size):
                    father[(r, c)] = (r, c)

            def find(pos):
                if father[pos] != pos:
                    father[pos] = find(father[pos])
                return father[pos]

            def union(pos1, pos2):
                father[pos1] = pos2

            for r in range(board_size):
                for c in range(board_size):
                    for dir, move in enumerate(
                        self.moves[1:3]
                    ):  # Only check down and right
                        if self.chess_board[r, c, dir + 1]:
                            continue
                        pos_a = find((r, c))
                        pos_b = find((r + move[0], c + move[1]))
                        if pos_a != pos_b:
                            union(pos_a, pos_b)

            for r in range(board_size):
                for c in range(board_size):
                    find((r, c))
            my_r = find(tuple(self.my_pos))
            adv_r = find(tuple(self.adv_pos))
            my_score = list(father.values()).count(my_r)
            adv_score = list(father.values()).count(adv_r)
            if my_r == adv_r:
                return False, my_score, adv_score
            return True, my_score, adv_score
        def distance(self,child):
            """
            determine how far the move is to the oponent, scaled to a number from 0 to 1 by divided by the maximum steps can be taken to reach oponent
            """
            ra,ca=self.adv_pos
            rc,cc=child.my_pos
            return (abs(ra-rc)+abs(ca-cc)-1)/((len(self.chess_board)-1)*2)
        
        def barrier(self,child):
            """
            determine if the barrier is towards the oponent (0 if not, 1 if yes)
            example: if child's barrier is at 0 (up), return 1 if the oponent is above the child (ra<rc)
            """
            ra,ca=self.adv_pos
            rc,cc=child.my_pos
            if child.barrier_dir==0:
                    if ra<rc: return 1
            if child.barrier_dir==1:
                    if ca>cc: return 1
            if child.barrier_dir==2:
                    if ra>rc: return 1
            if child.barrier_dir==3:
                    if ca<cc: return 1
            return 0
                
        def center(self,child):
            """
            calculate distance from the child to the center. We will favour children who are closer to the center (guarantee at least a draw)
            we will use pythagoras theorem. Then scale this value to a number from 0 to 1 by divide with the furthest distance from center.
            """
            r,c=child.my_pos
            n=len(self.chess_board)
            center=math.floor(n/2)
            dist=math.sqrt(pow((r-center),2) + pow((c-center),2))
            return dist/math.sqrt(pow((0-center),2) + pow((0-center),2))

        def assign_val(self):
            """
            assign values for children based on heuristics and weights
            Return:
                None,
                if return a child -> choose it right away (winning move)
            """
            

            for child in self.children:
                is_end_game,c,ad=child.check_endgame() #check whether or not game ended after move
                if is_end_game:
                    if c>ad:
                        return child #return child that make us win
                    if c<=ad:
                        self.children.remove(child)      #remove all child that make us loose          
                h1=self.distance(child)
                h2=self.barrier(child)
                h3=self.center(child)
                value=2*h2-3*h1-h3 #calculate the total value by weighted heuristics
                child.value=value
            return None



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

        n1=self.Node(my_pos=my_pos,barrier_dir=None,chess_board=chess_board,value=0,adv_pos=adv_pos)
        n1.get_children()
        n1.assign_val()
        n1.children.sort(key=lambda x: x.value,reverse=True)
        pos=n1.children[0].my_pos
        d=n1.children[0].barrier_dir
        # dummy return
        return pos, d
