"""
checkers.py
A simple checkers engine written in Python with the pygame 1.9.1 libraries.
Here are the rules I am using: http://boardgames.about.com/cs/checkersdraughts/ht/play_checkers.htm
I adapted some code from checkers.py found at 
http://itgirl.dreamhosters.com/itgirlgames/games/Program%20Leaders/ClareR/Checkers/checkers.py starting on line 159 of my program.
This is the final version of my checkers project for Programming Workshop at Marlboro College. The entire thing has been rafactored and made almost completely object oriented.
Funcitonalities include:
- Having the pieces and board drawn to the screen
- The ability to move pieces by clicking on the piece you want to move, then clicking on the square you would
  like to move to. You can change you mind about the piece you would like to move, just click on a new piece of yours.
- Knowledge of what moves are legal. When moving pieces, you'll be limited to legal moves.
- Capturing
- DOUBLE capturing etc.
- Legal move and captive piece highlighting
- Turn changes
- Automatic kinging and the ability for them to move backwords
- Automatic check for and end game. 
- A silky smoooth 60 FPS!
Everest Witman - May 2014 - Marlboro College - Programming Workshop 
"""

import pygame, sys
from pygame.locals import *

import ai

pygame.font.init()

##COLORS##
#             R    G    B 
WHITE    = (255, 255, 255)
BLUE     = (  0,   0, 255)
RED      = (255,   0,   0)
BLACK    = (  0,   0,   0)
GOLD     = (255, 215,   0)
HIGH     = (160, 190, 255)

##DIRECTIONS##
NORTHWEST = "northwest"
NORTHEAST = "northeast"
SOUTHWEST = "southwest"
SOUTHEAST = "southeast"

monteCarlo = ai.MonteCarlo(ai.Board())

class Game:
	"""
	The main game control.
	"""

	def __init__(self):
		self.graphics = Graphics()
		self.board = Board()
		
		self.turn = BLUE
		self.selected_piece = None # a board location. 
		self.hop = False
		self.selected_legal_moves = []
		self.won = False

	def setup(self):
		"""Draws the window and board at the beginning of the game"""
		self.graphics.setup_window()

	def event_loop(self):
		"""
		The event loop. This is where events are triggered 
		(like a mouse click) and then effect the game state.
		"""
		self.mouse_pos = self.graphics.board_coords(pygame.mouse.get_pos()) # what square is the mouse in?
		if self.selected_piece != None:
			self.selected_legal_moves = self.board.all_legal_moves(self.selected_piece, self.hop)

		for event in pygame.event.get():

			if event.type == QUIT:
				self.terminate_game()

			if event.type == MOUSEBUTTONDOWN:
				if self.turn == BLUE:
					if self.hop == False:
						if self.board.location(self.mouse_pos).occupant != None and self.board.location(self.mouse_pos).occupant.color == self.turn:
							self.selected_piece = self.mouse_pos

						elif self.selected_piece != None and self.mouse_pos in self.board.all_legal_moves(self.selected_piece):

							if self.board.is_capture_move(self.selected_piece, self.mouse_pos) != (-1, -1):
								to_be_removed = self.board.is_capture_move(self.selected_piece, self.mouse_pos)
								self.board.remove_piece(to_be_removed)
								self.board.move_piece(self.selected_piece, self.mouse_pos)
							
								self.hop = True
								self.selected_piece = self.mouse_pos

							else:
								self.board.move_piece(self.selected_piece, self.mouse_pos)
								self.end_turn()

					if self.hop == True:					
						if self.selected_piece != None and self.mouse_pos in self.board.all_legal_moves(self.selected_piece, self.hop):
							to_be_removed = self.board.is_capture_move(self.selected_piece, self.mouse_pos)
							self.board.remove_piece(to_be_removed)
							self.board.move_piece(self.selected_piece, self.mouse_pos)

						if self.board.all_legal_moves(self.mouse_pos, self.hop) == []:
							self.end_turn()

						else:
							self.selected_piece = self.mouse_pos

	def update(self):
		"""Calls on the graphics class to update the game display."""
		self.graphics.update_display(self.board, self.selected_legal_moves, self.selected_piece)

	def terminate_game(self):
		"""Quits the program and ends the game."""
		pygame.quit()
		sys.exit

	def convert_hop(self, coord):
		return (7 - coord[1], coord[0])

	def convert_state(self, state):
		new_state = []

		for i in xrange(7, -1, -1):
			for j in xrange(8):
				if self.board.location((j, i)).occupant == None:
					new_state.append(0)
				elif self.board.location((j, i)).occupant.color == RED:
					if self.board.location((j, i)).occupant.king == True:
						new_state.append(-2)
					else:
						new_state.append(2)
				elif self.board.location((j, i)).occupant.color == BLUE:
					if self.board.location((j, i)).occupant.king == True:
						new_state.append(-1)
					else:
						new_state.append(1)
		
		if (self.hop == True):
			new_state.append(self.convert_hop(self.selected_piece))
		else:
			new_state.append((-1, -1))
		
		if (self.turn == BLUE):
			new_state.append(1)
		else:
			new_state.append(2)
		
		return tuple(new_state)
	
	def convert_action(self, action):
		return (action[1], 7 - action[0], action[3], 7 - action[2])

	def main(self):
		""""This executes the game and controls its flow."""
		self.setup()

		while True: # main game loop
			self.event_loop()
			self.update()

			if self.won == False and self.turn == RED:
				print 'Vez da IA jogar!!! Espere ela se preparar.'
				monteCarlo.update(self.convert_state(self.board.matrix))
				print 'Ela viu o jogo, agora ela precisa agir.'
				action = monteCarlo.get_play()
				print 'Jogada: ' + str(action)
				start_x, start_y, end_x, end_y = self.convert_action(action)

				if self.hop == False:
					self.selected_piece = (start_x, start_y)
					
					if self.board.is_capture_move(self.selected_piece, (end_x, end_y)) != (-1, -1):
						to_be_removed = self.board.is_capture_move(self.selected_piece, (end_x, end_y))
						self.board.remove_piece(to_be_removed)
						self.board.move_piece(self.selected_piece, (end_x, end_y))
						
						self.hop = True
						self.selected_piece = (end_x, end_y)
					else:
						self.board.move_piece(self.selected_piece, (end_x, end_y))
						self.end_turn()
				
				if self.hop == True:
					if self.selected_piece != None and (end_x, end_y) in self.board.all_legal_moves(self.selected_piece, self.hop):
						to_be_removed = self.board.is_capture_move(self.selected_piece, (end_x, end_y))
						self.board.remove_piece(to_be_removed)
						self.board.move_piece(self.selected_piece, (end_x, end_y))

					if self.board.all_legal_moves((end_x, end_y), self.hop) == []:
						self.end_turn()
					else:
						self.selected_piece = (end_x, end_y)

	def end_turn(self):
		"""
		End the turn. Switches the current player. 
		end_turn() also checks for and game and resets a lot of class attributes.
		"""
		if self.turn == BLUE:
			self.turn = RED
		else:
			self.turn = BLUE

		self.selected_piece = None
		self.selected_legal_moves = []
		self.hop = False

		if self.check_for_endgame():
			self.won = True
			if self.turn == BLUE:
				self.graphics.draw_message("RED WINS!")
			else:
				self.graphics.draw_message("BLUE WINS!")

	def check_for_endgame(self):
		"""
		Checks to see if a player has run out of moves or pieces. If so, then return True. Else return False.
		"""
		for x in xrange(8):
			for y in xrange(8):
				if self.board.location((x,y)).color == BLACK and self.board.location((x,y)).occupant != None and self.board.location((x,y)).occupant.color == self.turn:
					if self.board.all_legal_moves((x,y)) != []:
						return False

		return True

class Graphics:
	def __init__(self):
		self.caption = "Checkers"

		self.fps = 60
		self.clock = pygame.time.Clock()

		self.window_size = 600
		self.screen = pygame.display.set_mode((self.window_size, self.window_size))
		self.background = pygame.image.load('resources/board.png')

		self.square_size = self.window_size / 8
		self.piece_size = self.square_size / 2

		self.message = False

	def setup_window(self):
		"""
		This initializes the window and sets the caption at the top.
		"""
		pygame.init()
		pygame.display.set_caption(self.caption)

	def update_display(self, board, legal_moves, selected_piece):
		"""
		This updates the current display.
		"""
		self.screen.blit(self.background, (0,0))
		
		self.highlight_squares(legal_moves, selected_piece)
		self.draw_board_pieces(board)

		if self.message:
			self.screen.blit(self.text_surface_obj, self.text_rect_obj)

		pygame.display.update()
		self.clock.tick(self.fps)

	def draw_board_squares(self, board):
		"""
		Takes a board object and draws all of its squares to the display
		"""
		for x in xrange(8):
			for y in xrange(8):
				pygame.draw.rect(self.screen, board[x][y].color, (x * self.square_size, y * self.square_size, self.square_size, self.square_size), )
	
	def draw_board_pieces(self, board):
		"""
		Takes a board object and draws all of its pieces to the display
		"""
		for x in xrange(8):
			for y in xrange(8):
				if board.matrix[x][y].occupant != None:
					pygame.draw.circle(self.screen, board.matrix[x][y].occupant.color, self.pixel_coords((x,y)), self.piece_size) 

					if board.location((x,y)).occupant.king == True:
						pygame.draw.circle(self.screen, GOLD, self.pixel_coords((x,y)), int (self.piece_size / 1.7), self.piece_size / 4)


	def pixel_coords(self, board_coords):
		"""
		Takes in a tuple of board coordinates (x,y) 
		and returns the pixel coordinates of the center of the square at that location.
		"""
		return (board_coords[0] * self.square_size + self.piece_size, board_coords[1] * self.square_size + self.piece_size)

	def board_coords(self, (pixel_x, pixel_y)):
		"""
		Does the reverse of pixel_coords(). Takes in a tuple of of pixel coordinates and returns what square they are in.
		"""
		return (pixel_x / self.square_size, pixel_y / self.square_size)	

	def highlight_squares(self, squares, origin):
		"""
		Squares is a list of board coordinates. 
		highlight_squares highlights them.
		"""
		for square in squares:
			pygame.draw.rect(self.screen, HIGH, (square[0] * self.square_size, square[1] * self.square_size, self.square_size, self.square_size))	

		if origin != None:
			pygame.draw.rect(self.screen, HIGH, (origin[0] * self.square_size, origin[1] * self.square_size, self.square_size, self.square_size))

	def draw_message(self, message):
		"""
		Draws message to the screen. 
		"""
		self.message = True
		self.font_obj = pygame.font.Font('freesansbold.ttf', 44)
		self.text_surface_obj = self.font_obj.render(message, True, HIGH, BLACK)
		self.text_rect_obj = self.text_surface_obj.get_rect()
		self.text_rect_obj.center = (self.window_size / 2, self.window_size / 2)

class Board:
	def __init__(self):
		self.matrix = self.new_board()

	def new_board(self):
		"""
		Create a new board matrix.
		"""

		# initialize squares and place them in matrix

		matrix = [[None] * 8 for i in xrange(8)]

		# The following code block has been adapted from
		# http://itgirl.dreamhosters.com/itgirlgames/games/Program%20Leaders/ClareR/Checkers/checkers.py
		for x in xrange(8):
			for y in xrange(8):
				if (x % 2 != 0) and (y % 2 == 0):
					matrix[y][x] = Square(WHITE)
				elif (x % 2 != 0) and (y % 2 != 0):
					matrix[y][x] = Square(BLACK)
				elif (x % 2 == 0) and (y % 2 != 0):
					matrix[y][x] = Square(WHITE)
				elif (x % 2 == 0) and (y % 2 == 0): 
					matrix[y][x] = Square(BLACK)

		# initialize the pieces and put them in the appropriate squares

		for x in xrange(8):
			for y in xrange(3):
				if matrix[x][y].color == BLACK:
					matrix[x][y].occupant = Piece(RED)
			for y in xrange(5, 8):
				if matrix[x][y].color == BLACK:
					matrix[x][y].occupant = Piece(BLUE)

		return matrix

	def board_string(self, board):
		"""
		Takes a board and returns a matrix of the board space colors. Used for testing new_board()
		"""

		board_string = [[None] * 8] * 8 

		for x in xrange(8):
			for y in xrange(8):
				if board[x][y].color == WHITE:
					board_string[x][y] = "WHITE"
				else:
					board_string[x][y] = "BLACK"


		return board_string
	
	def rel(self, dir, (x,y)):
		"""
		Returns the coordinates one square in a different direction to (x,y).
		===DOCTESTS===
		>>> board = Board()
		>>> board.rel(NORTHWEST, (1,2))
		(0,1)
		>>> board.rel(SOUTHEAST, (3,4))
		(4,5)
		>>> board.rel(NORTHEAST, (3,6))
		(4,5)
		>>> board.rel(SOUTHWEST, (2,5))
		(1,6)
		"""
		if dir == NORTHWEST:
			return (x - 1, y - 1)
		elif dir == NORTHEAST:
			return (x + 1, y - 1)
		elif dir == SOUTHWEST:
			return (x - 1, y + 1)
		elif dir == SOUTHEAST:
			return (x + 1, y + 1)
		else:
			return 0
	
	def get_dir(self, (x1,y1), (x2,y2)):
		if (x1 < x2):
			if (y1 < y2):
				return SOUTHEAST
			else:
				return NORTHEAST
		else:
			if (y1 < y2):
				return SOUTHWEST
			else:
				return NORTHWEST
	
	def is_capture_move(self, (x1,y1), (x2,y2)):
		move = (x1, y1)
		dir = self.get_dir(move, (x2,y2))
		while (move[0] != x2) and (move[1] != y2):
			if (self.location(move).occupant != None):
				if (self.location(move).occupant.color != self.location((x1,y1)).occupant.color):
					return move
			move = self.rel(dir, move)
		return (-1,-1)

	def adjacent(self, (x,y)):
		"""
		Returns a list of squares locations that are adjacent (on a diagonal) to (x,y).
		"""

		return [self.rel(NORTHWEST, (x,y)), self.rel(NORTHEAST, (x,y)),self.rel(SOUTHWEST, (x,y)),self.rel(SOUTHEAST, (x,y))]

	def location(self, (x,y)):
		"""
		Takes a set of coordinates as arguments and returns self.matrix[x][y]
		This can be faster than writing something like self.matrix[coords[0]][coords[1]]
		"""

		return self.matrix[x][y]

	def blind_legal_moves(self, (x,y)):
		"""
		Returns a list of blind legal move locations from a set of coordinates (x,y) on the board. 
		If that location is empty, then blind_legal_moves() return an empty list.
		"""

		if self.matrix[x][y].occupant != None:
			blind_legal_moves = [self.rel(NORTHWEST, (x,y)), self.rel(NORTHEAST, (x,y)), self.rel(SOUTHWEST, (x,y)), self.rel(SOUTHEAST, (x,y))]
		else:
			blind_legal_moves = []

		return blind_legal_moves
	
	def is_capture_move_feasible(self, dir, (x1,y1), (x2,y2)):
		if self.location((x2,y2)).occupant.color != self.location((x1,y1)).occupant.color:
			if dir == NORTHWEST or dir == NORTHEAST or dir == SOUTHWEST or dir == SOUTHEAST:
				possible_move = self.rel(dir, (x2,y2))
				if self.on_board(possible_move) and self.location(possible_move).occupant == None:
					return True

		return False

	def legal_moves(self, (x,y), hop = False):
		"""
		Returns a list of legal move locations from a given set of coordinates (x,y) on the board.
		If that location is empty, then legal_moves() returns an empty list.
		"""

		blind_legal_moves = self.blind_legal_moves((x,y))

		directions = [NORTHWEST, NORTHEAST, SOUTHWEST, SOUTHEAST]
		legal_moves = []

		if hop == False:
			if blind_legal_moves != []:
				for i in xrange(4):
					move = blind_legal_moves[i]
					if hop == False:
						if self.location((x,y)).occupant.king == True:
							enemySeen = False
							while self.on_board(move):
								if self.location(move).occupant == None:
									legal_moves.append(move)
									move = self.rel(directions[i], move)
									continue
								elif enemySeen == False and self.is_capture_move_feasible(directions[i], (x,y), move):
									legal_moves.append(self.rel(directions[i], move))
									enemySeen = True
									move = self.rel(directions[i], self.rel(directions[i], move))
									continue
								elif self.location(move).occupant.color == self.location((x,y)).occupant.color:
									break
								else:
									break
						else:
							if self.on_board(move):
								if self.location(move).occupant == None:
									if self.location((x,y)).occupant.color == RED:
										if i > 1:
											legal_moves.append(move)
									elif self.location((x,y)).occupant.color == BLUE:
										if i < 2:
											legal_moves.append(move)
								elif self.is_capture_move_feasible(directions[i], (x,y), move): # is this location filled by an enemy piece?
									legal_moves.append(self.rel(directions[i], move))
		else: # hop == True
			for i in xrange(4):
				move = blind_legal_moves[i]
				if self.location((x,y)).occupant.king == True:
					enemySeen = False
					while self.on_board(move):
						if self.location(move).occupant == None:
							move = self.rel(directions[i], move)
							continue
						elif enemySeen == False and self.is_capture_move_feasible(directions[i], (x,y), move):
							legal_moves.append(self.rel(directions[i], move))
							enemySeen = True
							move = self.rel(directions[i], self.rel(directions[i], move))
							continue
						elif self.location(move).occupant.color == self.location((x,y)).occupant.color:
							break
						else:
							break
				else:							
					if self.on_board(move) and self.location(move).occupant != None:
						if self.is_capture_move_feasible(directions[i], (x,y), move): # is this location filled by an enemy piece?
							legal_moves.append(self.rel(directions[i], move))
		return legal_moves
	
	def all_legal_moves(self, (x, y), hop = False):
		capture_moves = []

		for i in xrange(8):
			for j in xrange(8):
				if self.location((i, j)).occupant != None and self.location((i, j)).occupant.color == self.location((x, y)).occupant.color:
					legal_moves = self.legal_moves((i, j), hop)

					if legal_moves != []:
						for move in legal_moves:
							if self.is_capture_move((i,j), move) != (-1, -1):
								capture_moves.append(move)
		
		legal_moves = self.legal_moves((x, y), hop)

		if capture_moves != []:
			capture_moves = []
			for move in legal_moves:
				if self.is_capture_move((x, y), move) != (-1, -1):
					capture_moves.append(move)
			return capture_moves
		else:
			return legal_moves

	def remove_piece(self, (x,y)):
		"""
		Removes a piece from the board at position (x,y). 
		"""
		self.matrix[x][y].occupant = None

	def move_piece(self, (start_x, start_y), (end_x, end_y)):
		"""
		Move a piece from (start_x, start_y) to (end_x, end_y).
		"""

		self.matrix[end_x][end_y].occupant = self.matrix[start_x][start_y].occupant
		self.remove_piece((start_x, start_y))

		self.king((end_x, end_y))

	def is_end_square(self, coords):
		"""
		Is passed a coordinate tuple (x,y), and returns true or 
		false depending on if that square on the board is an end square.
		===DOCTESTS===
		>>> board = Board()
		>>> board.is_end_square((2,7))
		True
		>>> board.is_end_square((5,0))
		True
		>>>board.is_end_square((0,5))
		False
		"""

		if coords[1] == 0 or coords[1] == 7:
			return True
		else:
			return False

	def on_board(self, (x,y)):
		"""
		Checks to see if the given square (x,y) lies on the board.
		If it does, then on_board() return True. Otherwise it returns false.
		===DOCTESTS===
		>>> board = Board()
		>>> board.on_board((5,0)):
		True
		>>> board.on_board(-2, 0):
		False
		>>> board.on_board(3, 9):
		False
		"""

		if x < 0 or y < 0 or x > 7 or y > 7:
			return False
		else:
			return True

	def king(self, (x,y)):
		"""
		Takes in (x,y), the coordinates of square to be considered for kinging.
		If it meets the criteria, then king() kings the piece in that square and kings it.
		"""
		if self.location((x,y)).occupant != None:
			if (self.location((x,y)).occupant.color == BLUE and y == 0) or (self.location((x,y)).occupant.color == RED and y == 7):
				self.location((x,y)).occupant.king = True 

class Piece:
	def __init__(self, color, king = False):
		self.color = color
		self.king = king

class Square:
	def __init__(self, color, occupant = None):
		self.color = color # color is either BLACK or WHITE
		self.occupant = occupant # occupant is a Square object

def main():
	game = Game()
	game.main()

if __name__ == "__main__":
	main()