from __future__ import division

import time
from random import choice
from math import log, sqrt

##DIRECTIONS##
NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"

class Board(object):
    def start(self):
        start = (   0, 1, 0, 1, 0, 1, 0, 1,
                    1, 0, 1, 0, 1, 0, 1, 0,
                    0, 1, 0, 1, 0, 1, 0, 1,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0, 0,
                    2, 0, 2, 0, 2, 0, 2, 0,
                    0, 2, 0, 2, 0, 2, 0, 2,
                    2, 0, 2, 0, 2, 0, 2, 0, (-1, -1), 1)
        return start

    def current_player(self, state):
        return state[-1]

    def remove_piece(self, state, (x,y)):
        state[8 * x + y] = 0
        return state

    def king(self, state, (x,y)):
        if state[8 * x + y] != 0:
            if (state[8 * x + y] == 2 and x == 0) or (state[8 * x + y] == 1 and x == 7):
                state[8 * x + y] = state[8 * x + y] * (-1)
        return state

    def next_state(self, state, play):
        hop = (-1, -1)
        start_x, start_y, end_x, end_y = play
        player = state[-1]
        state = list(state)
        capture = self.is_capture_move(state, play)
        if capture != (-1, -1):
            state = self.remove_piece(state, capture)
            legal_moves = self.all_legal_moves(tuple(state))
            if legal_moves != []:
                for move in legal_moves:
                    if (move[0] == end_x) and (move[1] == end_y) and self.is_capture_move(state, move) != (-1, -1):
                        hop = (end_x, end_y)
        state[8 * end_x + end_y] = state[8 * start_x + start_y]
        state = self.remove_piece(state, (start_x, start_y))
        state = self.king(state, (end_x, end_y))
        state[-2] = hop
        if hop == (-1, -1):
            state[-1] = 3 - player
        return tuple(state)
    
    def rel(self, dir, move):
        x1, y1, x2, y2 = move
        if dir == NORTHWEST:
			return (x1, y1, x2 + 1, y2 - 1)
        elif dir == NORTHEAST:
			return (x1, y1, x2 + 1, y2 + 1)
        elif dir == SOUTHWEST:
			return (x1, y1, x2 - 1, y2 - 1)
        elif dir == SOUTHEAST:
			return (x1, y1, x2 - 1, y2 + 1)
        else:
			return 0
    
    def blind_legal_moves(self, state, (x,y)):
        if state[8 * x + y] != 0:
            blind_legal_moves = [self.rel(NORTHWEST, (x,y,x,y)), self.rel(NORTHEAST, (x,y,x,y)), self.rel(SOUTHWEST, (x,y,x,y)), self.rel(SOUTHEAST, (x,y,x,y))]
        else:
			blind_legal_moves = []
        return blind_legal_moves

    def on_board(self, (x,y)):
		if x < 0 or y < 0 or x > 7 or y > 7:
			return False
		else:
			return True
    
    def is_capture_move_feasible(self, state, dir, move):
        x1,y1,x2,y2 = move
        if abs(state[8 * x2 + y2]) != abs(state[8 * x1 + y1]):
			if dir == NORTHWEST or dir == NORTHEAST or dir == SOUTHWEST or dir == SOUTHEAST:
				possible_move = self.rel(dir, move)
				if self.on_board((possible_move[2], possible_move[3])) and state[8 * possible_move[2] + possible_move[3]] == 0:
					return True
        return False
    
    def legal_moves(self, state, (x,y)):
        blind_legal_moves = self.blind_legal_moves(state, (x,y))
        directions = [NORTHWEST, NORTHEAST, SOUTHWEST, SOUTHEAST]
        legal_moves = []
        hop = state[-2]

        if hop == (-1, -1):
            if blind_legal_moves != []:
                for i in xrange(4):
                    move = blind_legal_moves[i]
                    move_x, move_y = move[2], move[3]
                    if hop == (-1, -1):
                        if state[8 * x + y] < 0:
                            enemySeen = False
                            while self.on_board((move_x, move_y)):
                                if state[8 * move_x + move_y] == 0:
                                    legal_moves.append(move)
                                    move = self.rel(directions[i], move)
                                    move_x, move_y = move[2], move[3]
                                    continue
                                elif enemySeen == False and self.is_capture_move_feasible(state, directions[i], move):
                                    legal_moves.append(self.rel(directions[i], move))
                                    enemySeen = True
                                    move = self.rel(directions[i], self.rel(directions[i], move))
                                    move_x, move_y = move[2], move[3]
                                    continue
                                elif abs(state[8 * move_x + move_y]) == abs(state[8 * x + y]):
                                    break
                                else:
                                    break
                        else:
                            if self.on_board((move_x, move_y)):
                                if state[8 * move_x + move_y] == 0:
                                    if abs(state[8 * x + y]) == 2:
                                        if i > 1:
                                            legal_moves.append(move)
                                    elif abs(state[8 * x + y]) == 1:
                                        if i < 2:
                                            legal_moves.append(move)
                                elif self.is_capture_move_feasible(state, directions[i], move): # is this location filled by an enemy piece?
                                    legal_moves.append(self.rel(directions[i], move))
        else: # hop == True
            for i in xrange(4):
                move = blind_legal_moves[i]
                move_x, move_y = move[2], move[3]
                if state[8 * x + y] < 0:
                    enemySeen = False
                    while self.on_board((move_x, move_y)):
                        if state[8 * move_x + move_y] == 0:
                            move = self.rel(directions[i], move)
                            move_x, move_y = move[2], move[3]
                            continue
                        elif enemySeen == False and self.is_capture_move_feasible(state, directions[i], move):
                            legal_moves.append(self.rel(directions[i], move))
                            enemySeen = True
                            move = self.rel(directions[i], self.rel(directions[i], move))
                            move_x, move_y = move[2], move[3]
                            continue
                        elif abs(state[8 * move_x + move_y]) == abs(state[8 * x + y]):
                            break
                        else:
                            break
                else:
                    if self.on_board((move_x, move_y)) and state[8 * move_x + move_y] != 0:
                        if self.is_capture_move_feasible(state, directions[i], move): # is this location filled by an enemy piece?
                            legal_moves.append(self.rel(directions[i], move))
        return legal_moves

    def get_dir(self, move):
        x1, y1, x2, y2 = move
        if (x1 < x2):
			if (y1 < y2):
				return NORTHEAST
			else:
				return NORTHWEST
        else:
			if (y1 < y2):
				return SOUTHEAST
			else:
				return SOUTHWEST
	
    def is_capture_move(self, state, move):
        dir = self.get_dir(move)
        m = (move[0], move[1], move[0], move[1])
        x, y = m[2], m[3]
        while (x != move[2]) and (y != move[3]):
            if state[8 * x + y] != 0:
                if abs(state[8 * x + y]) != abs(state[8 * move[0] + move[1]]):
                    return (x, y)
            m = self.rel(dir, m)
            x, y = m[2], m[3]
        return (-1,-1)

    def all_legal_moves(self, state):
        legal_moves = []
        capture_moves = []
        player = state[-1]

        for i in xrange(8):
            for j in xrange(8):
                if state[8 * i + j] != 0 and abs(state[8 * i + j]) == player:
                    legal_moves.extend(self.legal_moves(state, (i, j)))
                    if legal_moves != []:
                        for move in legal_moves:
                            if self.is_capture_move(state, move) != (-1, -1):
                                capture_moves.append(move)

        if capture_moves != []:
            return capture_moves
        else:
            return legal_moves

    def legal_plays(self, state_history):
        state = state_history[-1]
        return self.all_legal_moves(state)

    def check_for_endgame(self, state):
        if self.all_legal_moves(state) != []:
            return False
        return True

    def winner(self, state_history):
        state = state_history[-1]
        player = state[-1]
        if self.check_for_endgame(state):
            if player == 1:
                return 2
            elif player == 2:
                return 1
        return 0

class MonteCarlo(object):
    def __init__(self, board, **kwargs):
        self.calculation_time = kwargs.get('time', 2)
        self.max_moves = kwargs.get('max_moves', 1000)
        self.C = kwargs.get('C', 1.4)

        self.board = board
        self.states = [self.board.start()]
        self.wins = {}
        self.plays = {}
        self.max_depth = 0

    def update(self, state):
        self.states.append(state)

    def get_play(self):
        state = self.states[-1]
        player = self.board.current_player(state)
        legal = self.board.legal_plays(self.states[:])

        if not legal:
            return
        if len(legal) == 1:
            return legal[0]

        games = 0
        begin = time.time()
        while time.time() - begin < self.calculation_time:
            self.run_simulation()
            games += 1

        moves_states = [(p, self.board.next_state(state, p)) for p in legal]

        print str(games) + ' ' + str(time.time() - begin)

        percent_wins, move = max(
            (
                self.wins.get((player, S), 0) / self.plays.get((player, S), 1),
                p
            ) for p, S in moves_states
        )

        for x in sorted(
            ((100 * self.wins.get((player, S), 0) / self.plays.get((player, S), 1),
            self.wins.get((player, S), 0),
            self.plays.get((player, S), 0),
            p)
                for p, S in moves_states),
                reverse=True
        ):
            print "{3}: {0:.2f}% ({1}/{2})".format(*x)

        print "Maximum depth searched: " + str(self.max_depth)

        return move

    def run_simulation(self):
        plays, wins = self.plays, self.wins

        visited_states = set()
        states_copy = self.states[:]
        state = states_copy[-1]
        player = self.board.current_player(state)

        expand = True
        for t in range(1, self.max_moves + 1):
            legal = self.board.legal_plays(states_copy)
            moves_states = [(p, self.board.next_state(state, p)) for p in legal]

            if all(plays.get((player, S)) for p, S in moves_states):
                log_total = log(
                    sum(plays[(player, S)] for p, S in moves_states))
                value, move, state = max(
                    ((wins[(player, S)] / plays[(player, S)]) +
                    self.C * sqrt(log_total / plays[(player, S)]), p, S)
                    for p, S in moves_states
                )
            else:
                move, state = choice(moves_states)

            states_copy.append(state)

            if expand and (player, state) not in plays:
                expand = False
                plays[(player, state)] = 0
                wins[(player, state)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, state))

            player = self.board.current_player(state)
            winner = self.board.winner(states_copy)
            if (winner):
                break

        for player, state in visited_states:
            if (player, state) not in plays:
                continue
            plays[(player, state)] += 1
            if (player == winner):
                wins[(player, state)] += 1

m = MonteCarlo(Board())
m.get_play()