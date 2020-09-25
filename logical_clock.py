# the main part of the program is taken from 
# https://towardsdatascience.com/understanding-lamport-timestamps-with-pythons-multiprocessing-library-12a6427881c6

from multiprocessing import Process, Pipe
from os import getpid
from datetime import datetime

def get_process_name(pid):
	if pid == 0:
		return 'a'
	elif pid == 1:
		return 'b'
	elif pid == 2:
		return 'c'
	else:
		return 'unknown error'

def local_time(counter):
	return f'(LAMPORT_TIME={counter})'

def calc_recv_timestamp(recv_time_stamp, counter):
	for id  in range(len(counter)):
		counter[id] = max(recv_time_stamp[id], counter[id])
	return counter

def event(pid, counter):
	counter[pid] += 1
	print(f'Something happened in {get_process_name(pid)} ! {local_time(counter)}')
	return counter

def send_message(pipe, pid, counter):
	counter[pid] += 1
	pipe.send(('Empty shell', counter))
	print(f'Message sent from {get_process_name(pid)} {local_time(counter)}')
	return counter

def recv_message(pipe, pid, counter):
	counter[pid] += 1
	message, timestamp = pipe.recv()
	counter = calc_recv_timestamp(timestamp, counter)
	print(f'Message received at {get_process_name(pid)} {local_time(counter)}')
	return counter

def a(pipe12):
	pid = 0
	counter = [0,0,0]
	counter = send_message(pipe12, pid, counter)
	counter = send_message(pipe12, pid, counter)
	counter = event(pid, counter)
	counter = recv_message(pipe12, pid, counter)
	counter = event(pid, counter)
	counter = event(pid, counter)
	counter = recv_message(pipe12, pid, counter)
	print(f'Final state of process {get_process_name(pid)} is {counter}')


def b(pipe21, pipe23):
	pid = 1
	counter = [0,0,0]
	counter = recv_message(pipe21, pid, counter)
	counter = recv_message(pipe21, pid, counter)
	counter = send_message(pipe21, pid, counter)
	counter = recv_message(pipe23, pid, counter)
	counter = event(pid, counter)
	counter = send_message(pipe21, pid, counter)
	counter = send_message(pipe23, pid, counter)
	counter = send_message(pipe23, pid, counter)
	print(f'Final state of process {get_process_name(pid)} is {counter}')


def c(pipe32):
	pid = 2
	counter = [0,0,0]
	counter = send_message(pipe32, pid, counter)
	counter = recv_message(pipe32, pid, counter)
	counter = event(pid, counter)
	counter = recv_message(pipe32, pid, counter)
	print(f'Final state of process {get_process_name(pid)} is {counter}')




if __name__ == '__main__':
	ab, ba = Pipe()
	bc, cb = Pipe()

	process1 = Process(target=a, args=(ab,))
	process2 = Process(target=b, args=(ba, bc))
	process3 = Process(target=c, args=(cb,))

	process1.start()
	process2.start()
	process3.start()

	process1.join()
	process2.join()
	process3.join()
