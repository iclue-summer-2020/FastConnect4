import numpy as np
import random
from functools import reduce
from statistics import stdev
from math import sqrt
import multiprocessing
import time

product = lambda arr: reduce(lambda a,b: a*b, arr)

# Class that stores a random variable in the form 1/n \sum_{i=0}^n f(g_i)
# We take the average as well as sample some values to calculate std. dev.
class RandomVariable:
	def __init__(self, sample_rate):
		self.N = 0
		self.total = 0
		self.samples = []
		self.sample_rate = sample_rate
	def update(self, val):
		self.N += 1
		self.total += val
		if self.N % self.sample_rate == 0:
			self.samples.append(val)
	def get_mean(self):
		return self.total / self.N
	def get_error(self):
		return stdev(self.samples) / len(self.samples) if len(self.samples) > 1 else -1
# Initialize random variables from https://arxiv.org/pdf/1901.11161.pdf
X = RandomVariable(100) # used to calculate game tree size
Y = RandomVariable(100) # used to calculate game length
Z = RandomVariable(100) # used to calculate draw rate
P1 = RandomVariable(100) # used to calculate p1 win rate
P2 = RandomVariable(100) # used to calculate p2 win rate


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
	return (product(game.possible_move_vector), game.get_win(), game.moves)


def process_result(results):
	global X
	global Y
	global Z
	global P1
	global P2
	product, winner, moves = results
	X.update(product)
	Y.update(product*len(moves))
	Z.update(product*1 if winner=="tie" else 0)
	P1.update(product*1 if winner=="player 1" else 0)
	P2.update(product*1 if winner=="player 2" else 0)

def run():
	number_cores = int(input("Enter number of cores (0 to use all): "))
	if number_cores == 0: number_cores = multiprocessing.cpu_count()
	pool = multiprocessing.Pool(number_cores)
	number_runs = int(input("Enter number of trials per core: "))
	for _ in range(number_runs):
		pool.apply_async(get_possible_position_vector, args = (), callback = process_result)
	pool.close()
	pool.join()
	print("Game tree size: ", X.get_mean())
	print("Average game length: ", Y.get_mean() / X.get_mean())
	print("Draw rate: ", Z.get_mean() / X.get_mean())
	print("P1 win rate: ", P1.get_mean() / X.get_mean())
	print("P2 win rate: ", P2.get_mean() / X.get_mean())
