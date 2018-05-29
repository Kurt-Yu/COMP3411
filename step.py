'''
!/usr/bin/python3

This file is a host socket, used to communicate with agent,
read in a file, then process it and pass the 24 characters string to agent,
and then wait for a action, finally based on that action, update our map.
Do those steps over and over again if the socket is open.

Usage: python3 step.py 31415 s0.in
'''

import sys
import socket

def get_agent(game):            # get the current coordinate of agent
    for i in range(len(game)):
        for j in range(len(game[0])):
            if game[i][j] == '^' or game[i][j] == 'v' or game[i][j] == '<' or game[i][j] == '>':
                return i, j

def rotate(view, time):         # rotate 2d list clockwise once
    for i in range(time):
        temp = zip(*view[::-1])               # return a list of tuples
        view = [list(elem) for elem in temp]  # convert list of tuples to list of lists
    view[2][2] = '^'
    return view

def get_view(game):
    x, y = get_agent(game)     # (x, y) is the coordinate of the agent

    view = [[0 for i in range(5)] for j in range(5)]   # initlize a 2d list
    for i in range(5):
        for j in range(5):
            temp_x, temp_y = x - 2 + i, y - 2 + j
            if temp_x < 0 or temp_y < 0 or temp_x >= len(game) or temp_y >= len(game[0]):
                view[i][j] = '.'
            else:
                view[i][j] = game[temp_x][temp_y]
    if view[2][2] == 'v':       # if agent is 'v', rotate twice
        view = rotate(view, 2)
    if view[2][2] == '<':       # if agent is '<', rotate once
        view = rotate(view, 1)
    if view[2][2] == '>':
        view = rotate(view, 3)

    return view

# this function converts a 2d list into a single string (without agent, only 24 characters)
def get_view_string(view):
    view_list = [y for x in view for y in x]   # convert 2d list into a single list
    temp = ''.join(map(str, view_list))        # convert this list into a string
    for i in ['^', 'v', '<', '>']:             # the for loop is used to get rid of the agent, just pass the rest 24 characters
        if i in temp:
            view_string = temp.replace(i, '')
            return view_string

def pick_up(temp):
    global inventory
    for i in ['a', 'k', 'o', '$']:
        if i == temp:
            inventory[i] += 1
            break

def chop_tree(x, y):
    global game
    global inventory
    if game[x][y] == 'T':
        game[x][y] = ' '
        if inventory['r'] == 0:
            inventory['r'] += 1

def unlock_door(x, y):
    global game
    if game[x][y] == '-':
        game[x][y] = ' '

port = int(sys.argv[1])
filename = sys.argv[2]

game = []       # game is a 2d array that stores the elements of whole map
with open(filename) as f:
    for line in f:
        game.append(list(line)[:-1])

inventory = {'a':0, 'k':0, 'o':0, '$':0, 'r':0}   # Initialise the inventory using a dictionary
pickable = ['a', 'k', 'o', '$']
stepping_stone = False        # these two variables are used to track if the agent is on
raft = False                  # a stepping stone or a raft

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # create a TCP socket
sock.bind(('localhost', port))   # bind the socket to the port
sock.listen(5)                   # listen for incoming connections
conn, addr = sock.accept()

while True:
    print('\n'.join(map(''.join, game)))
    x, y = get_agent(game)
    view = get_view(game)
    view_string = get_view_string(view)
    conn.sendall(view_string.encode())    # sent the 24 characters

    action = conn.recv(1024).decode()     # receive the action that agent choose
    print("\naction = {0}\n".format(action))
    if action == 'l' or action == 'L':
        if game[x][y] == '^':
            game[x][y] = '<'
        elif game[x][y] == 'v':
            game[x][y] = '>'
        elif game[x][y] == '<':
            game[x][y] = 'v'
        else:
            game[x][y] = '^'

    if action == 'r' or action == 'R':
        if game[x][y] == '^':
            game[x][y] = '>'
        elif game[x][y] == 'v':
            game[x][y] = '<'
        elif game[x][y] == '<':
            game[x][y] = '^'
        else:
            game[x][y] = 'v'

    if action == 'f' or action == 'F':
        if game[x][y] == '^':
            m = x - 1
            n = y
        elif game[x][y] == 'v':
            m = x + 1
            n = y
        elif game[x][y] == '<':
            m = x
            n = y - 1
        else:
            m = x
            n = y + 1

        if game[m][n] == ' ':
            if stepping_stone:
                game[x][y], game[m][n] = 'O', game[x][y]
            elif raft:
                game[x][y], game[m][n] = '~', game[x][y]
            else:
                game[x][y], game[m][n] = ' ', game[x][y]
            stepping_stone = False
            raft = False

        if game[m][n] == 'O':
            if stepping_stone:
                game[x][y], game[m][n] = 'O', game[x][y]
            elif raft:
                game[x][y], game[m][n] = '~', game[x][y]
                stepping_stone = True
                raft = False
            else:
                game[x][y], game[m][n] = ' ', game[x][y]
                stepping_stone = True

    if game[m][n] in pickable:
        temp = game[m][n]
        if stepping_stone:
            game[x][y], game[m][n] = 'O', game[x][y]
            stepping_stone = False
        elif raft:
            game[x][y], game[m][n] = '~', game[x][y]
            raft = False
        else:
            game[x][y], game[m][n] = ' ', game[x][y]
        pick_up(temp)

    if game[m][n] == '~':
        if raft:
            game[x][y], game[m][n] = '~', game[x][y]
            continue

        if inventory['r'] <= 0 and inventory['o'] <= 0:
            print("You dropped into river. Game over.")
            sock.close()
        if inventory['o'] > 0:
            if stepping_stone:
                game[x][y], game[m][n] = 'O', game[x][y]
            else:
                game[x][y], game[m][n] = ' ', game[x][y]
                stepping_stone = True
            inventory['o'] -= 1
            continue
        if inventory['o'] <= 0 and inventory['r'] > 0:
            raft = True
            inventory['r'] -= 1
            if stepping_stone:
                game[x][y], game[m][n] = 'O', game[x][y]
            else:
                game[x][y], game[m][n] = ' ', game[x][y]

    if action == 'c' or action == 'C':
        if inventory['a'] <= 0:
            continue
        if game[x][y] == '^':
            chop_tree(x - 1, y)
        if game[x][y] == 'v':
            chop_tree(x + 1, y)
        if game[x][y] == '<':
            chop_tree(x, y - 1)
        if game[x][y] == '>':
            chop_tree(x, y + 1)

    if action == 'u' or action == 'U':
        if inventory['k'] <= 0:
            continue

        if game[x][y] == '^':
            unlock_door(x - 1, y)
        if game[x][y] == 'v':
            unlock_door(x + 1, y)
        if game[x][y] == '<':
            unlock_door(x, y - 1)
        if game[x][y] == '>':
            unlock_door(x, y + 1)



