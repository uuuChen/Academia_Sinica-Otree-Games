# import random
#
# players = [1, 2, 3, 4, 5, 6]
# random.shuffle(players)
# groups = list()
# rightCounter = 0
# for i in range(0, len(players), 3):
#     if i + 3 > len(players):
#         break
#     groups.append(players[i: i+3])
#     if rightCounter < len(players) % 3:
#         groups[-1].append(players[-1-rightCounter])
#         rightCounter += 1
# print(groups)


a = "12345" + "6789"

b = 6789
a = f'12345' + b
print(a)