import numpy as np
import random
from functools import reduce
from statistics import stdev
from math import sqrt
import multiprocessing
import time
from collections import Counter
from tqdm import tqdm
import sys

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
		if self.sample_rate != 0:
			if self.N % self.sample_rate == 0:
				self.samples.append(val)
	def get_mean(self):
		return self.total / self.N
	def get_error(self):
		return stdev(self.samples) / len(self.samples) if len(self.samples) > 1 else -1
# Initialize random variables from https://arxiv.org/pdf/1901.11161.pdf
X = RandomVariable(0) # used to calculate game tree size
Y = RandomVariable(0) # used to calculate game length
Z = RandomVariable(0) # used to calculate draw rate
P1 = RandomVariable(0) # used to calculate p1 win rate
P2 = RandomVariable(0) # used to calculate p2 win rate
N = 0
temp = 0
p1wins = 0
p2wins = 0
ties = 0
# Progress bar
pbar = None
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
FULL_BOARD = 558517276622718
FULL_HEIGHTS = [6,13,20,27,34,41,48]
class Connect4Game:
	def __init__(self):
		self.bitboards = [0,0]
		self.heights = [0,7,14,21,28,35,42]
		self.counter = 0
		self.moves = []
		self.possible_move_vector = []
		self.move_list = [0,1,2,3,4,5,6]
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
		if not self.get_win() and col in self.move_list:
			self.possible_move_vector.append(len(self.move_list))
			self.heights[col] += 1
			move = rotate_left(1, self.heights[col])
			self.bitboards[self.counter % 2] ^= move
			self.moves.append(col)
			self.counter += 1
			if self.heights[col] == FULL_HEIGHTS[col]: self.move_list.remove(col)
		else:
			raise ValueError("game finished!")
	# We don't need this per se, it's just here for completeness
	def undo_move(self):
		self.counter -= 1
		col = self.moves[-1]
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
			game.make_move(random.choice(game.move_list))
		except:
			break
	out = (product(game.possible_move_vector), game.get_win(), game.moves)
	del game
	return out


def process_result(results):
	global X
	global Y
	global Z
	global P1
	global P2
	global N
	global temp
	global p1wins
	global p2wins
	global draws
	global pbar
	global ties
	pbar.update(1)
	product, winner, moves = results
	X.update(product)
	Y.update(product*len(moves))
	Z.update(product if winner=="tie" else 0)
	P1.update(product if winner=="player 1" else 0)
	P2.update(product if winner=="player 2" else 0)
	N += 1
	temp += len(moves)
	if winner == "player 1": p1wins += 1
	if winner == "player 2": p2wins += 1
	if winner == "tie": ties += 1
def run(number_cores, number_runs, number_batches):
	global pbar
	if number_cores == 0: number_cores = multiprocessing.cpu_count()
	pbar = tqdm(total=number_runs*number_batches, file=sys.stdout)
	start = time.time()
	for batch in range(number_batches):
		pool = multiprocessing.Pool(number_cores)
		for _ in range(number_runs):
			pool.apply_async(get_possible_position_vector, args = (), callback = process_result)
		pool.close()
		pool.join()
	print("Game tree size: ", X.get_mean(), " with error ", X.get_error())
	print("Average game length: ", Y.get_mean() / X.get_mean())
	print("Draw rate: ", Z.get_mean() / X.get_mean())
	print("P1 win rate: ", P1.get_mean() / X.get_mean())
	print("P2 win rate: ", P2.get_mean() / X.get_mean())
	print("Average game length (actual): ", temp/N)
	print("P1 wins: ", p1wins/N)
	print("P2 wins: ", p2wins/N)
	print("Ties: ", ties / N)
	print("Total number of games: ", N)
	print("Time elapsed: ", time.time()-start)

def run_input():
	number_cores = int(input("Enter number of cores (0 to use all): "))
	number_runs = int(input("Enter number of trials per batch: "))
	number_batches = int(input("Enter number of batches: "))
	run(number_cores, number_runs, number_batches)

def test():
	out = 0
	for i in range(100000):
		print(i)
		out += get_possible_position_vector()[0]
	return out

