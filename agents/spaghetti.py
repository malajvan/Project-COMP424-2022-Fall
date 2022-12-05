# Student agent: Add your own agent here
from agents.agent import Agent
from store import register_agent
import sys
from math import sqrt
import numpy as np
from random import randint, seed
from time import time
from copy import deepcopy
 
 
@register_agent("spaghetti_agent")
class SpaAgent(Agent):
    """
    A dummy class for your implementation. Feel free to use this class to
    add any helper functionalities needed for your agent.
    """
 
    def find_all_possible_path(self, k,l,chess_board,pos, adv_pos):
        if (k >0):
            if (pos[0]-1 >= 0):  #up 
                if (not(chess_board[pos[0], pos[1], 0]) and ((pos[0]-1,pos[1]) != adv_pos)):
                    l += (self.find_all_possible_path(k-1,l, chess_board, (pos[0]-1, pos[1]), adv_pos))
 
            if (pos[0]+1 < len(chess_board) ):  #down
                if (not(chess_board[pos[0], pos[1], 2]) and ((pos[0]+1,pos[1]) != adv_pos)):
                    l  += (self.find_all_possible_path(k-1,l, chess_board, (pos[0]+1, pos[1]), adv_pos))
 
            if (pos[1]+1 < len(chess_board)):  #right
                if (not(chess_board[pos[0], pos[1], 1]) and ((pos[0],pos[1]+1) != adv_pos)):
                    l += (self.find_all_possible_path(k-1,l, chess_board, (pos[0], pos[1]+1), adv_pos))
 
            if (pos[1]-1 >= 0 ):  #left
                if (not(chess_board[pos[0], pos[1], 3]) and ((pos[0],pos[1]-1) != adv_pos)):
                    l += (self.find_all_possible_path(k-1,l, chess_board, (pos[0], pos[1]-1), adv_pos))
 
        statesss = []
        for i in range(4):
            if not(chess_board[pos[0],pos[1], i]):
                statesss.append((pos, i))
        l += statesss
 
        return statesss
 
    def check_endgame(self, board_size, my_pos, adv_pos, turn, chess_board):
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
                    if chess_board[r, c, dir + 1]:
                        continue
                    pos_a = find((r, c))
                    pos_b = find((r + move[0], c + move[1]))
                    if pos_a != pos_b:
                        union(pos_a, pos_b)
 
        for r in range(board_size):
            for c in range(board_size):
                find((r, c))
        p0_r = find(tuple(my_pos))
        p1_r = find(tuple(adv_pos))
        p0_score = list(father.values()).count(p0_r)
        p1_score = list(father.values()).count(p1_r)
        if p0_r == p1_r:
            return False, -1
        player_win = None
        if p0_score > p1_score:
            if turn:
                return True, 1
            else:
                return True, 0
        elif p0_score < p1_score:
            if turn:
                return True, 0
            else:
                return True, 1
        else:
            return True, 0.5
    
    def check_valid_step(self, start_pos, end_pos, barrier_dir , chess_board ,adv_pos, K):
        """
        Check if the step the agent takes is valid (reachable and within max steps).
        Parameters
        ----------
        start_pos :np.ndarray
            The start position of the agent.
        end_pos : np.ndarray
            The end position of the agent.
        barrier_dir : int
            The direction of the barrier.
        """
        # Endpoint already has barrier or is boarder
        r, c = end_pos
        if chess_board[r, c, barrier_dir]:
            return False
        if np.array_equal(start_pos, end_pos):
            return True
 
        # Get position of the adversary
 
 
        # BFS
        state_queue = [(start_pos, 0)]
        visited = {tuple(start_pos)}
        is_reached = False
        while state_queue and not is_reached:
            cur_pos, cur_step = state_queue.pop(0)
            #print(cur_pos)
            r, c = cur_pos
            if cur_step == K:
                break
            for dir, move in enumerate(self.moves):
                if chess_board[r, c, dir]:
                    continue
 
                next_pos = cur_pos + move
                if np.array_equal(next_pos, adv_pos) or tuple(next_pos) in visited:
                    continue
                if np.array_equal(next_pos, end_pos):
                    is_reached = True
                    break
 
                visited.add(tuple(next_pos))
                state_queue.append((next_pos, cur_step + 1))
 
 
        return is_reached
 
    def get_possible_moves(self, chess_board, my_pos, adv_pos, max_step):
        all_possible_pos =[]
 
        self.find_all_possible_path(max_step,all_possible_pos,chess_board,my_pos,adv_pos)
 
        new_set = set(all_possible_pos)
        all_possible_pos = list(new_set)
        for state in all_possible_pos:
            booleanval = self.check_valid_step(np.asarray(my_pos), np.asarray(state[0]), state[1], chess_board,adv_pos, max_step)
 
            if booleanval == False:
                all_possible_pos.remove(state)
        return all_possible_pos
 
    def get_pid(self):
        self.pid += 1
        return self.pid
 
    def find_best(self):
        best_pid = -1
        best_score = -1
        for i in self.dict:
            if self.dict[i].score > best_score:
                best_score = self.dict[i].score
                best_pid = i
        return best_pid
 
    class Node:
        
        def __init__(self, chess_board, my_pos, adv_pos, turn, parent=None, super_parent_pid=None, move=None, tier=None):
            self.parent = parent
            self.wins = 0
            self.visits = 1
            self.score = 0
            self.chess_board = chess_board
            self.my_pos = my_pos
            self.adv_pos = adv_pos
            self.turn = turn
            self.super_parent_pid = super_parent_pid
            self.move = move
            self.tier = tier
 
    
    def score(self, node):
        qsa = 0
        if node.visits != 0:
            qsa = node.wins/node.visits
            # print(f'visits: {node.visits}')
            # print(f'parent visits: {node.parent.visits}')
            # print(f'qsa: {qsa}')
            return qsa + sqrt(2*np.log(node.parent.visits)/node.visits)
        else:
            return 0
        # When switching root nodes, set root note parent to None
        # When initializing the initial step, create a parent node with its parent = None
 
    def set_barrier(self, chess_board, r, c, dir):
        # Set the barrier to True
        chess_board[r, c, dir] = True
        # Set the opposite barrier to True
        move = self.moves[dir]
        chess_board[r + move[0], c + move[1], self.opposites[dir]] = True
        return chess_board
 
    def back_prop(self, state, result):
        state.wins += result
        state.visits += 1
        cur = state
        while cur.parent != None:
            cur.parent.wins += result
            cur.parent.visits += 1
            # cur.parent.score = self.score(cur.parent)
            # cur.score = self.score(cur)
            cur = cur.parent
        # l = [(1,1)]
        # tmp = set(playable_moves)
        for i in self.dict:
            # if self.dict[i] in tmp:
            #     add to l
            self.dict[i].score = self.score(self.dict[i])
 
    def run_simulation(self, state, max_step):
        # Current iteration is adversary's turn
        # Choose best state to expand
        # Have to check if current state is endgame, if endgame then can't expand
        # state = self.dict[self.find_best()]
        # From best state, find random state
        # Get possible moves has to indicate who's turn it is
        # print(state.chess_board)
        # print(f'my_pos: {state.my_pos}')
        # print(f'adv_pos: {state.adv_pos}')
        # print(f'turn: {state.turn}')
        possible_moves = self.get_possible_moves(state.chess_board, state.my_pos, state.adv_pos, max_step)
        # print(possible_moves[:10])
        # print(possible_moves)
        random_move = possible_moves[randint(0, len(possible_moves)-1)]
        update_board = self.set_barrier(deepcopy(state.chess_board), random_move[0][0], random_move[0][1], random_move[1])
        state_node = self.Node(update_board, state.adv_pos, random_move[0], (not state.turn), state, -1, random_move,state.parent.tier-1)
        # if state_node.turn:
        #     print(f'B: {state_node.my_pos}, A: {state_node.adv_pos}, move: {state_node.move}')
        # else:
        #     print(f'B: {state_node.adv_pos}, A: {state_node.my_pos}, move: {state_node.move}')
        # print(f'board shape: {state_node.chess_board.shape[0]}')
        end, point = self.check_endgame(state_node.chess_board.shape[0], state_node.my_pos, state_node.adv_pos, state_node.turn, state_node.chess_board)
        if end:
            return point
        return self.run_simulation(state_node, max_step)
 
    def find_best_move(self, move_list):
        best_value = 0
        best_move = move_list[0]
        for i in move_list:
            if i.visits == 0:
                continue
            if i.wins / i.visits > best_value:
                best_value = i.wins / i.visits
                best_move = i
        return best_move
    
    def update_super(self, state):
        if state.tier == 0:
            return state.super_parent_pid
        state.super_parent_pid = self.update_super(state.parent)
        return state.super_parent_pid
 
    def __init__(self):
        super(SpaAgent, self).__init__()
        self.autoplay = True
        self.name = "SpaAgent"
        self.dir_map = {
            "u": 0,
            "r": 1,
            "d": 2,
            "l": 3,
        }
        # self.pid = -99999999
        self.pid = 0
        self.dict = {}
        self.update = {}
        self.playable = set()
        # self.reuse_list = []
        self.parent_node = self.Node(None, None, None, True)
        self.first_turn = True
        # Moves (Up, Right, Down, Left)
        self.moves = ((-1, 0), (0, 1), (1, 0), (0, -1))
        # seed(0) # SET SEED SDFSDFSD
 
        # Opposite Directions
        self.opposites = {0: 2, 1: 3, 2: 0, 3: 1}
 
    def step(self, chess_board, my_pos, adv_pos, max_step):
        start_time = time()
        # Update dictionary
        playable_moves = []
        tmp_id, tmp_state = None, None
        for i in self.dict:
            if (self.dict[i].chess_board == chess_board).all():
                tmp_state = self.dict[i]
                tmp_id = i
        if tmp_state != None:
            self.parent_node = tmp_state
            self.playable = set()
            tmp_dict = {}
            super_update_list = []
            for i in self.update[self.parent_node.super_parent_pid]:
                tmp_dict[i] = self.dict[i]
                # Playable
                if tmp_dict[i].parent == self.parent_node:
                    tmp_dict[i].tier = 1
                    tmp_dict[i].super_parent_pid = i
                    # self.reuse_list.append(tmp_dict[i])
                    self.playable.add(self.dict[i].move)
                    playable_moves.append(tmp_dict[i])
                else:
                    super_update_list.append(i)
            for i in super_update_list:
                if self.dict[i].parent.tier == 1:
                    self.dict[i].tier = 0
                self.update_super(self.dict[i])
            self.dict = tmp_dict
            self.parent_node.parent = None
            self.parent_node.super_parent_pid = None
        else:
            self.playable = set()
            self.dict = {}
            self.parent_node = self.Node(None, None, None, True)
        if len(chess_board) > 9:
            allowed_time = 0.8
            if self.first_turn == True:
                allowed_time = 23
                self.first_turn = False
        else:
            allowed_time = 1.5
            if self.first_turn == True:
                allowed_time = 26
                self.first_turn = False
        # update self.update, self.dict, self.parent_node
        self.update = {}
        moves = self.get_possible_moves(chess_board, my_pos, adv_pos, max_step)
        # Here
        if not self.first_turn:
            self.parent_node.visits = len(moves)
        best_move = moves[0]
        # no_suicide_moves = []
        # forced_suicide = False
        for i in moves:
            if i not in self.playable:
                # This iteration is our turn
                pid = self.get_pid()
                # has to be a chess state
                update_board = self.set_barrier(deepcopy(chess_board), i[0][0], i[0][1], i[1])
                state = self.Node(update_board, adv_pos, i[0],False, self.parent_node, pid, i, 1)
                end, point = self.check_endgame(state.chess_board.shape[0], state.my_pos, state.adv_pos, state.turn, state.chess_board)
                if end and point == 1:
                    return state.move
                if point != 0:
                    playable_moves.append(state)
                    self.dict[pid] = state
        if len(playable_moves) == 0:
            return best_move
        # for i in playable_moves:
        #     end, point = self.check_endgame(i.chess_board.shape[0], i.my_pos, i.adv_pos, i.turn, i.chess_board)
        #     if end and point == 1:
        #         return i.move
        #     if point != 0:
        #         no_suicide_moves.append(i)
        # for i in self.reuse_list:
        #     self.update[i.super_parent_pid] = []
        #     playable_moves.append(i)
        max_time = time() - start_time
        # i = 0
        run_index = 0
        run_once_length = len(playable_moves)
        while max_time < allowed_time:
        # while i < 60:
            # if my_pos == (1,1) and i == 0:
            #     print("HERE")
            #     pass
            # Current iteration is adversary's turn
            # Choose best state to expand
            # Have to check if current state is endgame, if endgame then can't expand
            # state = None
            if self.first_turn:
                if run_index < run_once_length:
                    state = playable_moves[run_index]
                    state.wins = 0
                    state.visits = 0
                    run_index += 1
                else:
                    state = self.dict[self.find_best()]
 
            end, point = self.check_endgame(state.chess_board.shape[0], state.my_pos, state.adv_pos, state.turn, state.chess_board)
            if end:
                self.back_prop(state, point)
                max_time = time() - start_time
                # i += 1
                continue
            # From best state, find random state
            # Get possible moves has to indicate who's turn it is
            possible_moves = self.get_possible_moves(state.chess_board, state.my_pos, state.adv_pos, max_step)
            random_move = possible_moves[randint(0, len(possible_moves)-1)]
            update_board = self.set_barrier(deepcopy(state.chess_board), random_move[0][0], random_move[0][1], random_move[1])
            tmp_pid = self.get_pid()
            if state.tier == 1:
                state_node = self.Node(update_board, state.adv_pos, random_move[0], (not state.turn), state, tmp_pid, random_move, 0)
            else:
                state_node = self.Node(update_board, state.adv_pos, random_move[0], (not state.turn), state, state.super_parent_pid, random_move, -1)
 
            # if state_node.turn:
            #     print(f'B: {state_node.my_pos}, A: {state_node.adv_pos}, move: {state_node.move}')
            # else:
            #     print(f'B: {state_node.adv_pos}, A: {state_node.my_pos}, move: {state_node.move}')
            end, point = self.check_endgame(state_node.chess_board.shape[0], state_node.my_pos, state_node.adv_pos, state_node.turn, state_node.chess_board)
            if end:
                self.back_prop(state_node, point)
            else:
                # Run simulation
                result = self.run_simulation(state_node, max_step)
                self.back_prop(state_node, result)
            # Add new state to dictionary and update list after back propagation
            self.dict[tmp_pid] = state_node
            if state_node.tier == 0:
                self.update[tmp_pid] = []
            else:
                self.update[state_node.super_parent_pid].append(tmp_pid)
            max_time = time() - start_time
            # i += 1
        
        best_move = self.find_best_move(playable_moves).move
        # Update dictionary
        # tmp_dict = {}
        # self.playable = set()
        # self.reuse_list = []
        # super_update_list = []
        # for i in self.update[self.parent_node.super_parent_pid]:
        #     tmp_dict[i] = self.dict[i]
        #     if tmp_dict[i].parent == self.parent_node:
        #         tmp_dict[i].super_parent_pid = i
        #         self.reuse_list.append(tmp_dict[i])
        #     else:
        #         super_update_list.append(i)
        #     self.playable.add(self.dict[i].move)
        # for i in super_update_list:
        #     self.update_super(self.dict[i], self.parent_node.super_parent_pid)
        # self.dict = tmp_dict
        # self.parent_node.parent = None
        # self.parent_node.super_parent_pid = None
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
        # print(time() - start_time)
        return best_move[0], best_move[1]