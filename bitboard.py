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
class Connect4Game:
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

def get_possible_position_vector():
	game = Connect4Game()
	while True:
		try:
			game.make_move(random.randrange(7))
		except:
			break
	return (game.possible_move_vector, game.get_win(), game.moves)

a = [get_possible_position_vector() for i in range(500)]
