import os
import json
import random
import copy

class UndoStack:
    def __init__(self, limit=10):
        self.stack = []
        self.limit = limit

    def push(self, item):
        # self.stack.append(item)
        self.stack.append(copy.deepcopy(item))

        if len(self.stack) > self.limit:
            self.stack = self.stack[-self.limit:]

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            return None

    def is_empty(self):
        return len(self.stack) == 0

dict_stack = UndoStack()
keys_stack = UndoStack()
max_stack = UndoStack()

os.chdir(os.path.dirname(os.path.abspath(__file__)))

if os.path.exists('save.json') and os.path.getsize('save.json') > 0:
    with open('save.json', 'r') as file:
        big_dict = json.load(file)

    m_dict = big_dict["matchups"]
    m_keys = big_dict["keys"]
    max_rounds = big_dict["max_rounds"]

else:

    txt_file = open('list.txt', 'r')

    text_list = txt_file.read().splitlines()

    big_dict = {"matchups": {}, "keys": [], "max_rounds": 0}
    
    m_dict = big_dict["matchups"]

    max_rounds = big_dict["max_rounds"]

    for item in text_list:
        m_dict[item] = [1000, 0]

    m_keys = list(m_dict)
    big_dict["keys"] = m_keys

    with open('save.json', 'w') as file:
        json.dump(big_dict, file)

if len(m_dict) < 3:
    pass # end program

TOTAL_ITEMS = len(m_keys)

def calculate_elo():

    difference = m_dict[loser][0] - m_dict[winner][0]

    base_mov = 15

    multiplier = 2 - 2 / (1 + 10**(difference / 100))

    movement = round(base_mov * multiplier)

    m_dict[winner][0] += movement
    m_dict[loser][0] -= movement

    if m_dict[loser][0] < 100:
        m_dict[loser][0] = 100

def calculate_rounds():
    global max_rounds
    global m_dict
    global m_keys

    m_dict[winner][1] += 1
    if m_dict[winner][1] > max_rounds:
        m_keys.remove(winner)
    m_dict[loser][1] += 1
    if m_dict[loser][1] > max_rounds:
        m_keys.remove(loser)

    if len(m_keys) < 2:
        max_rounds += 1
        m_keys = list(m_dict)

def order_items():
    sorted_dict = sorted(m_dict.items(), key=lambda x: x[1], reverse=True)

    with open('rankings.txt', 'w') as file:
        for key, value in sorted_dict:
            file.write(f"{key}: {value}\n")

    big_dict["matchups"] = m_dict
    big_dict["keys"] = m_keys
    big_dict["max_rounds"] = max_rounds

    with open('save.json', 'w') as file:
        json.dump(big_dict, file)

def generate_matchups():
    num_range = 15

    matchup_1 = random.choice(m_keys)
    matchup_2 = random.choice(m_keys)

    while matchup_1 == matchup_2 or abs(m_dict[matchup_1][0] - m_dict[matchup_2][0]) > num_range:
        matchup_2 = random.choice(m_keys)
        if matchup_1 != matchup_2:
            num_range += 10

    return matchup_1, matchup_2

while True:

    matchup_1, matchup_2 = generate_matchups()
    
    answer = input(matchup_1 + " [a] vs. " + matchup_2 + " [b] ")

    if answer == "u":
        if len(dict_stack.stack) > 0:
            m_dict = dict_stack.pop()
            m_keys = keys_stack.pop()
            max_rounds = max_stack.pop()
            order_items()
        continue

    while answer != "a" and answer != "b":
        if answer == "s":
            matchup_1, matchup_2 = generate_matchups()
        else:
            print("Invalid Input")
        answer = input(matchup_1 + " [a] vs. " + matchup_2 + " [b] ")

    dict_stack.push(dict(m_dict))
    keys_stack.push(list(m_keys))
    max_stack.push(int(max_rounds))
    
    if answer == "a":
        winner = matchup_1
        loser = matchup_2
    elif answer == "b":
        winner = matchup_2
        loser = matchup_1

    calculate_elo()
    calculate_rounds()
    order_items()
