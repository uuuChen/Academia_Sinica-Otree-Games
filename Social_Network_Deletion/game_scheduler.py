import numpy as np


def game_scheduler(num_of_players, shuffle=False):
    # build players' ids
    player_ids = np.array(list(range(1, num_of_players + 1)))
    if shuffle:
        np.random.shuffle(player_ids)
    if num_of_players % 2 != 0:
        # add a virtual player so that the number of players is a multiple of 2
        player_ids = np.append(player_ids, -1)
        num_of_players += 1
    player_ids = player_ids.reshape(-1, 2)
    anchor_id = player_ids[0, 0]
    circle_ids = np.append(player_ids[1:, 0], list(reversed(player_ids[:, 1])))
    id2cirIdx = dict(zip(circle_ids, range(len(circle_ids))))
    cir_real_indices = ([(row, 0) for row in range(1, len(player_ids[1:, 0]) + 1)] +
                        [(row, 1) for row in range(len(player_ids[:, 1]) - 1, -1, -1)])
    cirIdx2realIdx = dict(zip(id2cirIdx.values(), cir_real_indices))

    # use two dicts to update each round scheduled players' ids
    rounds_scheduled_ids = list()
    for round in range(1, len(circle_ids)+1):
        print(f'--------- ROUND {round} ---------')
        sheduled_ids = np.zeros(player_ids.shape)
        sheduled_ids[0, 0] = anchor_id
        for id in circle_ids:
            i, j = cirIdx2realIdx[id2cirIdx[id]]
            sheduled_ids[i, j] = id
        sheduled_ids = [(int(a_id), int(b_id)) for a_id, b_id in sheduled_ids]
        rounds_scheduled_ids.append(sheduled_ids)
        circle_ids = np.append(circle_ids[-1], circle_ids[:-1])
        id2cirIdx = dict(zip(circle_ids, range(num_of_players - 1)))
        print(sheduled_ids)

    print(f'--------- RETURN ---------')
    print(rounds_scheduled_ids)
    return rounds_scheduled_ids


def game_scheduler2(num_of_players):
    selected_mask = np.zeros((num_of_players, num_of_players))
    for round in range(1, num_of_players):
        print(f'--------- ROUND {round} ---------')
        players_mask = np.zeros((num_of_players, num_of_players))
        for i in range(players_mask.shape[0]):
            players_mask[i, i+1:] = 1
        players_mask = np.where(selected_mask == 1, 0, players_mask)
        # print(players_mask)
        while True:
            left_indices = list(zip(np.where(players_mask == 1)[0], np.where(players_mask == 1)[1]))
            if not left_indices:  # empty
                break
            selected_index = left_indices[0]
            selected_mask[selected_index] = 1
            print(f'{players_mask}')
            print(f'selected_index: {selected_index}')
            players_mask[selected_index[0], :] = 0
            players_mask[:, selected_index[0]] = 0
            players_mask[selected_index[1], :] = 0
            players_mask[:, selected_index[1]] = 0


def main():
    num_of_players = 6
    game_scheduler(num_of_players, shuffle=False)
    game_scheduler2(num_of_players)


if __name__ == '__main__':
    main()
