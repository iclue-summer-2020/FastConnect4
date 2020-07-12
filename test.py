import numpy as np
import random

class Connect4GameArray:
	def __init__(self):
		self.board = np.zeros((6,7),dtype=int)
		self.won = None
		self.moves = []
		self.possible_move_vector = []
		self.turn = False
	def __str__(self):
		return str(self.board)
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
		
import numpy as np
import random

# Rotate let and rotate right functions from https://falatic.com/index.php/108/python-and-bitwise-rotation
def rotate_left(val, r_bits, max_bits=64):
	return (val << r_bits%max_bits) & (2**max_bits-1) | \
			((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))
def rotate_right(val, r_bits, max_bits=64):
	return ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
			(val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))

def is_win(bitboard):
	for direction in [1,7,6,8]:
		bb = bitboard & rotate_right(bitboard, direction)
		if bb & rotate_right(bb, 2*direction) != 0: return True
	return False
	
def bitboard_to_arr(bitboard):
	return np.flip(np.array([int(i) for i in bin(bitboard)[2:].zfill(63)]).reshape((9,7)).transpose(),axis=1)[:-1,:-2]

# Implementation of bitboard from https://github.com/denkspuren/BitboardC4/blob/master/BitboardDesign.md
FULL_BOARD = 279258638311359
class Connect4GameBitBoard:
	def __init__(self):
		self.bitboards = [0,0]
		self.heights = [0,7,14,21,28,35,42]
		self.counter = 0
		self.moves = []
		self.possible_move_vector = []
	def to_arr(self):
		return bitboard_to_arr(self.bitboards[0]) + 2*bitboard_to_arr(self.bitboards[1])
	def __str__(self):
		return str(self.to_arr())
	def get_win(self):
		if is_win(self.bitboards[0]): return "player 1"
		if is_win(self.bitboards[1]): return "player 2"
		if (self.bitboards[0] | self.bitboards[1]) & FULL_BOARD == FULL_BOARD: return "tie"
		return None
	def make_move(self,col):
		if not self.get_win():
			self.heights[col] += 1
			move = rotate_left(1, self.heights[col])
			self.bitboards[self.counter % 2] ^= move
			self.moves.append(col)
			self.counter += 1
			self.possible_move_vector.append(len(self.list_moves()))
		else:
			raise ValueError("game finished!")
	# We don't need this per se, it's just here for completeness
	def undo_move(self):
		self.counter -= 1
		col = moves[-1]
		self.moves.pop()
		self.heights[col] -= 1
		move = rotate_left(1, self.heights[col])
		self.bitboards[self.counter % 2] ^= move
	def list_moves(self):
		TOP = 283691315109952
		possible_moves = []
		for col in range(7):
			if TOP & (rotate_left(1, self.heights[col])) == 0: possible_moves.append(col)
		return possible_moves

def run_random_game():
	board_arr = Connect4GameArray()
	board_bit = Connect4GameBitBoard()
	moves = []
	while not board_arr.won:
		move = random.randrange(7)
		try:
			board_arr.place_piece(move)
			board_bit.make_move(move)
			if str(board_arr) != str(board_bit):
				print("Disagreement!")
				print("Board (array)")
				print(board_arr)
				print("Board (bitboard)")
				print(board_bit)
				print("moves: ", moves)
				return moves
			moves.append(move)
		except:
			continue
	return board_arr
	
def run_game(moves):
	board_arr = Connect4GameArray()
	board_bit = Connect4GameBitBoard()
	for move in moves:
		try:
			board_arr.place_piece(move)
			board_bit.make_move(move)
			if str(board_arr) != str(board_bit):
				print("Disagreement!")
				print("Board (array)")
				print(board_arr)
				print("Board (bitboard)")
				print(board_bit)
				print("moves: ", moves)
				return moves
			moves.append(move)
		except:
			continue
	return None
	

