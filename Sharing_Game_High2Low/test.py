import random
num_players = 6
initial_points_list = [int(2000 / num_players)] * num_players
initial_points_list[-1] += 2000 - initial_points_list[0] * num_players
for i in range(10000):
    p1 = random.randint(0, num_players-1)
    p2 = random.randint(0, num_players-1)
    if random.randint(0, 1) == 0:
        giver = p1
        receiver = p2
    else:
        giver = p2
        receiver = p1
    give_amount = random.randint(0, initial_points_list[giver])
    initial_points_list[giver] -= give_amount
    initial_points_list[receiver] += give_amount

