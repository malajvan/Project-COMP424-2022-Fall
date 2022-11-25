import numpy as np
class MCnodes: # check https://github.com/hayoung-kim/mcts-tic-tac-toe/blob/master/VanilaMCTS.py
        def __init__(self,my_pos,barrier_dir,adv_pos,value=0,n=0,tree=None,chess_board=None):
            """
            Initialize the nodes for Monte Carlo Tree Search
            """
            # logger.info(f"Initializing node {move}")

            self.value=value
            self.n=n
            self.chess_board=chess_board
            self.my_pos=my_pos
            self.adv_pos=adv_pos
            self.moves=((-1, 0), (0, 1), (1, 0), (0, -1))
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
                    if(r,c)==(1,1):
                        print("hi")
                    break
                for dir, move in enumerate(self.moves):
                    if self.chess_board[r, c, dir]:
                        continue

                    next_pos = (cur_pos[0] + move[0],cur_pos[1]+move[1])
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
            return(children) #need to first make them nodes and link them in tree but tested seems ok

def main():
    c=np.zeros((4,4,4),dtype=bool)
    c[0, :, 0] = True
    c[:, 0, 3] = True
    c[-1, :, 2] = True
    c[:, -1, 1] = True
    c[:, -1, 1] = True
    c[0,2,2]=True

    print(n1.get_children())


main()