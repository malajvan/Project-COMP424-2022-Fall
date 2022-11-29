import numpy as np
import math
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
        
        def assign_val(self):
            """
            assign values for children based on heuristics and weights
            Return:
                None,
                if return a child -> choose it right away (winning move)
            """
        
            def closeness(self,child):
                """
                determine how close the move is to the oponent
                """
                ra,ca=self.adv_pos
                rc,cc=child.my_pos
                return (abs(ra-rc)+abs(ca-cc))
            
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
                we will use pythagoras theorem 
                """
                r,c=child.my_pos
                n=len(self.chessboard)
                center=math.floor(n/2)
                dist=math.sqrt((r-center)^2 + (c-center)^2)
                return dist
            
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
                board_size=len(self.chessboard)
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


            for child in self.children:
                is_end_game,c,ad=child.check_endgame() #check whether or not game ended after move
                if is_end_game:
                    if c>ad:
                        return child #return child that make us win
                    if c<=ad:
                        self.children.remove(child)      #remove all child that make us loose          
                h1=self.closeness(child)
                h2=self.barrier(child)
                h3=self.center(child)
            return None





def main():
    c=np.zeros((5,5,4),dtype=bool)
    c[0, :, 0] = True
    c[:, 0, 3] = True
    c[-1, :, 2] = True
    c[:, -1, 1] = True
    c[:, -1, 1] = True
    # c[0,0,2]=True
    n1=MCnodes((0,0),2,(1,1),0,0,chess_board=c)
    n1.get_children()



main()