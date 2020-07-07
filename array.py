import numpy as np
import random

class Connect4Game:
	def __init__(self):
		self.board = np.zeros((6,7),dtype=int)
		self.won = None
		self.moves = []
		self.possible_move_vector = []
		self.turn = False
	def get_possible_moves(self):
		return list(self.board[0]).count(0) # Just return the number of 0s in the first row of board
	def place_piece(self, col):
		turn = 1 if not self.turn else 2
		if not self.won:
			try:
				self.board[max(np.where(self.board[:,col]==0)[0])][col] = turn
				self.possible_move_vector.append(self.get_possible_moves())
				self.turn = not(self.turn)
				self.won = self.get_win()
				self.moves.append(col)
			except:
				raise ValueError("something went wrong! (probably full column)")
		else:
			raise ValueError("game finished!")
	def get_win(self):
		# return 1 if player 1 wins, 2 if player 2 wins, 3 if tie
		if self.get_possible_moves() == 0: return 3
		# Quick and dirty code to check for wins
		get_row = lambda b,i,j: [b[i][j], b[i][j+1], b[i][j+2], b[i][j+3]]
		get_col = lambda b,i,j: [b[i][j], b[i+1][j], b[i+2][j], b[i+3][j]]
		get_diag = lambda b,i,j: [b[i][j], b[i+1][j+1], b[i+2][j+2], b[i+3][j+3]]
		get_diag_ = lambda b,i,j: [b[i][j], b[i+1][j-1], b[i+2][j-2], b[i+3][j-3]]
		slices = []
		for i in range(6):
			for j in range(4):
				slices.append(get_row(self.board,i,j))
		for j in range(7):
			for i in range(3):
				slices.append(get_col(self.board,i,j))
		for i in range(3):
			for j in range(4):
				slices.append(get_diag(self.board,i,j))
		for i in range(3):
			for j in range(3,7):
				slices.append(get_diag_(self.board,i,j))
		potential_wins = [i for i in slices if len(set(i)) == 1 and 0 not in i]
		if len(potential_wins) == 0: return None
		else: return potential_wins[0][0]

def get_possible_position_vector():
	game = Connect4Game()
	while not game.won:
		try:
			game.place_piece(random.randrange(7))
		except:
			continue
	return (game.possible_move_vector, game.won, game.moves)

a = [get_possible_position_vector() for i in range(500)]
