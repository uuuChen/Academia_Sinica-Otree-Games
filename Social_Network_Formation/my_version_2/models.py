from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer
)

from django.forms import widgets
import math

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'my_version_1'
    num_rounds = 19  # it depends on the experiment
    players_per_group = None  # we maintain virtual group instead of otree group. "None" means all players are in the
                              # same otree group
    MAX_NUM_PLAYERS = 22  # it can be any number, but the bigger the number, the longer the program will run
    COST = 1  # cost of the game of stage 1
    BENEFIT = COST * 2  # benefit of the game of stage 1
    PRETEST_QUESTION_NUMS = 5
    PRETEST_ANSWERS = ['B', 'A', 'C', 'D', 'A']
    BASE_EARNED_NTD = 150
    NTD_GAP = 50
    NTD_PER_POINTS = 0.8
    QUESTIONNAIRE_QUESTION_NUMS = 3


class Subsession(BaseSubsession):

    def creating_session(self):

        # initialize all the attributes of all the players in the first round. There are descriptions of each
        # attribute in class 'Player'
        if self.round_number == 1:
            self.init_all_players_attributes()

    def init_all_players_attributes(self):

        num_players = self.session.num_participants  # "self.sesson.num_participants" -> this attribute is written by
                                                     # otree

        for id, player in list(enumerate(self.get_players(), start=1)):
            player.set_id(id=id)
            # player.set_participant_label(label='玩家' + str(id))
            # print(player.participant.label)
            # player.set_id(id=player.get_participant_label())
            player.set_total_points(points=0)

            # it's version 2, so in the beginning, all the other players' id will be in "others_id_not_in_group", and no
            # player's id will be in "others_id_in_group"
            others_id_in_group = []
            others_id_not_in_group = list(range(1, num_players + 1)).copy()
            others_id_not_in_group.remove(id) # remove current player's id him/herself
            player.set_others_id_in_group(id_list=others_id_in_group)  # empty
            player.set_others_id_not_in_group(id_list=others_id_not_in_group)  # all the other players' id

            player.set_is_game_over(is_game_over=False)  # not used
            player.set_last_stage_1_choice(choice='Nan')
            player.set_total_stage_1_playing_rounds(rounds=0)
            player.set_total_stage_1_given_rounds(rounds=0)
            player.set_last_stage_1_decisions_dict(init=True)
            player.set_last_stage_1_conn_nums(nums=0)
            player.set_last_stage_1_earned_points(points=0)
            player.set_last_stage_2_ori_conn_nums(nums=0)
            player.set_last_stage_2_end_conn_nums(nums=0)
            player.set_last_stage_2_add_conn_nums(nums=0)
            player.set_last_stage_2_send_conn_nums(nums=0)
            player.set_last_stage_2_rcv_conn_nums(nums=0)



class Group(BaseGroup):

    is_network_changed = models.BooleanField(initial=False)

    def trans_points_to_NTD(self):
        for cur_player in self.get_players():
            earned_NTD = Constants.BASE_EARNED_NTD + math.ceil(float(cur_player.get_total_points()) *
                Constants.NTD_PER_POINTS / Constants.NTD_GAP) * Constants.NTD_GAP
            cur_player.set_total_points(earned_NTD)

    def get_all_playing_players_id(self):
        return self.session.vars['playing_players_id']

    def set_all_playing_players_id(self, playing_players_id):
        self.session.vars['playing_players_id'] = playing_players_id

    def remove_playing_player_id(self, remove_player_id):
        playing_players_id = self.get_all_playing_players_id()
        if remove_player_id not in playing_players_id:
            return
        playing_players_id.remove(remove_player_id)
        self.set_all_playing_players_id(playing_players_id)

    def get_all_playing_players(self):
        return self.get_players_by_id_list(id_list=self.get_all_playing_players_id())

    def get_players_by_id_list(self, id_list):
        players = []
        for id in id_list:
            players.append(self.get_player_by_id(id))
        return players

    def compute_points_by_stage_1_results(self):
        for cur_player in self.get_players():
            total_earned_points = 0
            given_id_list = []
            non_given_id_list = []
            cur_coop_other = cur_player.coop_with_others

            # all players are required in the first round, so use function "get_others_not_in_group()", because all
            # other players don’t belong to the same group at the beginning
            if self.round_number == 1:
                other_players = cur_player.get_others_not_in_group()
                cur_player._others_id_in_group_record = str(cur_player.get_others_id_not_in_group())

            # other rounds have used connected players in the stage, so use function "get_others_in_group()"
            else:
                other_players = cur_player.get_others_in_group()
                cur_player._others_id_in_group_record = str(cur_player.get_others_id_in_group())

            for other_player in other_players:
                other_coop_cur = other_player.coop_with_others
                if other_coop_cur:
                    given_id_list.append(other_player.get_id())
                    if cur_coop_other:
                        earned_points = Constants.BENEFIT  # if two cooperate
                    else:
                        earned_points = Constants.COST + Constants.BENEFIT
                else:
                    non_given_id_list.append(other_player.get_id())
                    if cur_coop_other:
                        earned_points = 0
                    else:
                        earned_points = Constants.COST

                earned_points = earned_points
                total_earned_points += earned_points

            # if current player has connection with any player, maintain current player's total playing rounds and total
            # given rounds
            if len(other_players) != 0:
                # total playing rounds plus 1
                cur_player.set_total_stage_1_playing_rounds(cur_player.get_total_stage_1_playing_rounds() + 1)

                # if cur_coop_other is True, total given rounds plus 1
                if cur_coop_other:
                    cur_player.set_total_stage_1_given_rounds(cur_player.get_total_stage_1_given_rounds() + 1)
                    cur_player.set_last_stage_1_choice(choice='給')
                else:
                    cur_player.set_last_stage_1_choice(choice='不給')
            else:
                cur_player.set_last_stage_1_choice(choice='無')

            # maintain last_stage_1_decisions_dict. There are more details described in class 'Player' below
            dec_dict = {
                'given_id': given_id_list,
                'non_given_id': non_given_id_list
            }
            cur_player.set_last_stage_1_decisions_dict(decisions_dict=dec_dict)
            cur_player.set_total_points(points=cur_player.get_total_points() + total_earned_points)
            cur_player._total_points_records = int(cur_player.get_total_points())
            cur_player.set_last_stage_1_earned_points(points=total_earned_points)
            cur_player.set_last_stage_1_conn_nums(nums=cur_player.get_others_nums_in_group())

        if self.round_number == Constants.num_rounds:
            self.trans_points_to_NTD()

    def make_groups_by_stage_2_results(self):
        for cur_player in self.get_players():
            send_conn_nums = 0
            rcv_conn_nums = 0
            add_conn_nums = 0
            ori_conn_nums = cur_player.get_others_nums_in_group()
            for other_player in cur_player.get_others_not_in_group(): # get other players whom are not in the same group
                cur_player_id = cur_player.get_id()
                other_player_id = other_player.get_id()
                cur_conn_other = getattr(cur_player, 'connect_with_%s' % other_player_id)
                other_conn_cur = getattr(other_player, 'connect_with_%s' % cur_player_id)
                if cur_conn_other:
                    send_conn_nums += 1
                    if other_conn_cur:  # both connect to each other
                        rcv_conn_nums += 1
                        add_conn_nums += 1
                        cur_player.add_other_id_in_group(id=other_player_id)
                        cur_player.remove_other_id_not_in_group(id=other_player_id)
                    else:
                        pass
                else:
                    if other_conn_cur:
                        rcv_conn_nums += 1
                    else:
                        pass
            end_conn_nums = ori_conn_nums + add_conn_nums
            cur_player.set_last_stage_2_ori_conn_nums(nums=ori_conn_nums)
            cur_player.set_last_stage_2_end_conn_nums(nums=end_conn_nums)
            cur_player.set_last_stage_2_add_conn_nums(nums=add_conn_nums)
            cur_player.set_last_stage_2_send_conn_nums(nums=send_conn_nums)
            cur_player.set_last_stage_2_rcv_conn_nums(nums=rcv_conn_nums)


def make_checkbox_boolean_field():
    return models.BooleanField(widget=widgets.CheckboxInput())


def make_radio_select_boolean_field():
    return models.BooleanField(widget=widgets.RadioSelect)


def make_drop_down_menu_string_field(choices):
    return models.StringField(choices=choices)


def make_radio_select_string_field(choices=None):
    if choices:
        return models.StringField(widget=widgets.RadioSelect, choices=choices)
    else:
        return models.StringField(widget=widgets.RadioSelect)


class Player(BasePlayer):

    """

    Attribute:



        total_points (int): The points accumulated by the player so far.

        total_stage_1_playing_rounds (int): The total number of times the player has participated in stage 1. This
                                            attribute will be used in 'Stage_2.html'.

        total_stage_1_given_rounds (int): The total number of times the player has "given" to others in stage 1. This
                                          attribute will be used in 'Stage_2.html'.

        last_stage_1_conn_nums (int): The number of connections with the other players in last stage 1. This attribute
                                      will be used in 'Stage_1.html'.

        last_stage_1_earned_nums (int): The number of points the player earned in last stage 1. This attribute
                                        will be used in 'Stage_1.html'.

        last_stage_1_decisions_dict (dict): There are two keys, 'given_id' and 'non_given_id' in this dictionary
                                            respectively. 'given_id' stores the player id that selected "given" in
                                            the last round among the players connected to the player, and the remaining
                                            player's id are stored in "non_given_id". We can then use the function
                                            "get_players_by_id_list" in class "Group" to get "given" and "non_given"
                                            Player objects, and these objects will be used in 'Stage_1.html'.

        last_stage_2_ori_conn_nums (int): The number of players' connections before the start of stage 2. This
                                          attribute will be used in 'Stage_2_Results.html'.

        last_stage_2_end_conn_nums (int): The number of players' connections after playing stage 2. This
                                          attribute will be used in 'Stage_2_Results.html'.

        last_stage_2_add_conn_nums (int): The number of players' connections being added after playing stage 2. This
                                          attribute will be used in 'Stage_2_Results.html'.

        last_stage_2_send_conn_nums (int): The number of connection requests sent to other players in stage 2. This
                                           attribute will be used in 'Stage_2_Results.html'.

        last_stage_2_rcv_conn_nums (int): The number of connection requests received from other players in stage 2.
                                          This attribute will be used in 'Stage_2_Results.html'.

        others_id_in_group (list): A list of player's ids, which refers to ids of whom connected to current player.

        others_id_not_in_group (list): A list of player's ids, which refers to ids of whom not connected to current
                                       player.

        is_game_over (bool): Not used in this version.
    """
    _others_id_in_group_record = models.StringField()

    _total_points_records = models.IntegerField()

    coop_with_others = make_radio_select_boolean_field()

    consent = make_checkbox_boolean_field()

    questionnaire_1_options = make_radio_select_string_field([["男", "男"], ["女", "女"]])

    questionnaire_2_options = make_drop_down_menu_string_field([
        "20 歲以下",
        "21 歲",
        "22 歲",
        "23 歲",
        "24 歲",
        "25 歲",
        "26 歲",
        "27 歲",
        "28 歲",
        "29 歲",
        "30 歲",
        "30 歲以上",
    ])

    questionnaire_3_options = make_radio_select_string_field([
        "小於 10 人",
        "介於 10 至 19 人",
        "介於 20 至 29人",
        "介於 30 至 59人",
        "介於 50 至 99人",
        "介於 100 至 199人",
        "多於 200 人"
    ])

    for i in range(1, Constants.MAX_NUM_PLAYERS + 1):
        locals()["connect_with_%s" % i] = make_checkbox_boolean_field()
    del i

    for i in range(1, Constants.PRETEST_QUESTION_NUMS + 1):
        locals()["pretest_%s_options" % i] = make_radio_select_string_field()
    del i

    def get_id(self):
        return self.participant.vars['id']

    def get_total_points(self):
        return self.participant.payoff

    def get_participant_label(self):
        return self.participant.label

    def get_total_stage_1_playing_rounds(self):
        return self.participant.vars['total_stage_1_playing_rounds']

    def get_total_stage_1_given_rounds(self):
        return self.participant.vars['total_stage_1_given_rounds']

    def get_last_stage_1_choice(self):
        return self.participant.vars['last_stage_1_choice']

    def get_last_stage_1_conn_nums(self):
        return self.participant.vars['last_stage_1_conn_nums']

    def get_last_stage_1_earned_points(self):
        return self.participant.vars['last_stage_1_earned_points']

    def get_last_stage_1_decisions_dict(self):
        return self.participant.vars['last_stage_1_decisions_dict']

    def get_last_stage_2_ori_conn_nums(self):
        return self.participant.vars['last_stage_2_ori_conn_nums']

    def get_last_stage_2_end_conn_nums(self):
        return self.participant.vars['last_stage_2_end_conn_nums']

    def get_last_stage_2_add_conn_nums(self):
        return self.participant.vars['last_stage_2_add_conn_nums']

    def get_last_stage_2_send_conn_nums(self):
        return self.participant.vars['last_stage_2_send_conn_nums']

    def get_last_stage_2_rcv_conn_nums(self):
        return self.participant.vars['last_stage_2_rcv_conn_nums']

    def get_others_id_in_group(self):
        return self.participant.vars['others_id_in_group']

    def get_others_id_not_in_group(self):
        return self.participant.vars['others_id_not_in_group']

    def add_other_id_in_group(self, id):
        id_list = self.get_others_id_in_group()
        if id in id_list:
            return
        id_list.append(id)
        self.set_others_id_in_group(id_list=id_list)

    def add_other_id_not_in_group(self, id):
        id_list = self.get_others_id_not_in_group()
        if id in id_list:
            return
        id_list.append(id)
        self.set_others_id_in_group(id_list=id_list)

    def remove_other_id_in_group(self, id):
        id_list = self.get_others_id_in_group()
        if id not in id_list:
            return
        id_list.remove(id)
        self.set_others_id_in_group(id_list=id_list)

    def remove_other_id_not_in_group(self, id):
        id_list = self.get_others_id_not_in_group()
        if id not in id_list:
            return
        id_list.remove(id)
        self.set_others_id_not_in_group(id_list=id_list)

    def get_others_nums_in_group(self):
        return len(self.get_others_id_in_group())

    def get_others_nums_not_in_group(self):
        return len(self.get_others_id_not_in_group())

    def get_others_in_group(self):
        return self.group.get_players_by_id_list(id_list=self.get_others_id_in_group())

    def get_others_not_in_group(self):
        return self.group.get_players_by_id_list(id_list=self.get_others_id_not_in_group())

    def is_game_over(self):
        return self.participant.vars['is_game_over']

    def set_id(self, id):
        self.participant.vars['id'] = id

    def set_total_points(self, points):
        self.participant.payoff = points

    def set_participant_label(self, label):
        self.participant.label = label

    def set_total_stage_1_playing_rounds(self, rounds):
        self.participant.vars['total_stage_1_playing_rounds'] = rounds

    def set_total_stage_1_given_rounds(self, rounds):
        self.participant.vars['total_stage_1_given_rounds'] = rounds

    def set_last_stage_1_choice(self, choice):
        self.participant.vars['last_stage_1_choice'] = choice

    def set_last_stage_1_conn_nums(self, nums):
        self.participant.vars['last_stage_1_conn_nums'] = nums

    def set_last_stage_1_earned_points(self, points):
        self.participant.vars['last_stage_1_earned_points'] = points

    def set_last_stage_1_decisions_dict(self, decisions_dict=None, init=False):
        if init:
            decisions_dict = {
                'given_id': [],
                'non_given_id': [],
            }
        self.participant.vars['last_stage_1_decisions_dict'] = decisions_dict

    def set_last_stage_2_ori_conn_nums(self, nums):
        self.participant.vars['last_stage_2_ori_conn_nums'] = nums

    def set_last_stage_2_end_conn_nums(self, nums):
        self.participant.vars['last_stage_2_end_conn_nums'] = nums

    def set_last_stage_2_add_conn_nums(self, nums):
        self.participant.vars['last_stage_2_add_conn_nums'] = nums

    def set_last_stage_2_send_conn_nums(self, nums):
        self.participant.vars['last_stage_2_send_conn_nums'] = nums

    def set_last_stage_2_rcv_conn_nums(self, nums):
        self.participant.vars['last_stage_2_rcv_conn_nums'] = nums

    def set_others_id_in_group(self, id_list):
        self.participant.vars['others_id_in_group'] = id_list

    def set_others_id_not_in_group(self, id_list):
        self.participant.vars['others_id_not_in_group'] = id_list

    def set_is_game_over(self, is_game_over):
        self.participant.vars['is_game_over'] = is_game_over

    def get_stage_1_self_records(self):

        """ Get A list of self attributes to be displayed in 'Stage_1.html. '"""

        given_choice = self.get_last_stage_1_choice()
        conn_nums = self.get_last_stage_1_conn_nums()
        earned_points = self.get_last_stage_1_earned_points()
        return [given_choice, conn_nums, earned_points]

    def get_stage_1_conn_others_records(self, given):

        """ Get A list of connected others' attributes to be displayed in 'Stage_1.html. """

        dec_dict = self.get_last_stage_1_decisions_dict()
        key = 'given_id' if given else 'non_given_id'
        others_id_list = dec_dict[key]
        others_nums = len(others_id_list)
        others_avg_conns = 0
        others_avg_earned_points = 0

        # sum the numbers
        for other_player in self.group.get_players_by_id_list(id_list=others_id_list):
            others_avg_conns += other_player.get_last_stage_1_conn_nums()
            others_avg_earned_points += other_player.get_last_stage_1_earned_points()

        # count the average
        if others_nums != 0:  # avoid of dividing zero
            others_avg_conns /= others_nums
            others_avg_earned_points /= others_nums
        return [others_nums, others_avg_conns, others_avg_earned_points]

    def get_stage_2_non_conn_others_records(self):

        """ Get A list of non connected others' attributes to be displayed in 'Stage_2.html. """

        others_records = []
        for other_player in self.group.get_players_by_id_list(id_list=self.get_others_id_not_in_group()):
            id = other_player.get_id()
            total_given_rounds = other_player.get_total_stage_1_given_rounds()
            total_playing_rounds = other_player.get_total_stage_1_playing_rounds()
            other_records = [id, total_given_rounds, total_playing_rounds]
            others_records.append(other_records)
        return others_records

    def get_stage_2_results_self_records(self):

        """ Get A list of self attributes to be displayed in 'Stage_2_Results.html. """

        send_conn_nums = self.get_last_stage_2_send_conn_nums()
        rcv_conn_nums = self.get_last_stage_2_rcv_conn_nums()
        add_conn_nums = self.get_last_stage_2_add_conn_nums()
        ori_conn_nums = self.get_last_stage_2_ori_conn_nums()
        end_conn_nums = self.get_last_stage_2_end_conn_nums()
        return [send_conn_nums, rcv_conn_nums, add_conn_nums, ori_conn_nums, end_conn_nums]

    def have_any_connection(self):
        return True if len(self.get_others_id_in_group()) > 0 else False

    def have_full_connection(self):
        return True if len(self.get_others_id_not_in_group()) == 0 else False

    def coop_with_others_choices(self):
        return [
            [True, '給'],
            [False, '不給']
        ]














