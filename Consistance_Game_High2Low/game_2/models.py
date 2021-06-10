from otree.api import (
    models, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
)
import types
import statistics


author = 'Your name here'

doc = """
Your app description
"""

import math


class Constants(BaseConstants):
    name_in_url = 'game_2'
    num_rounds = 1000
    players_per_group = 2
    TOTAL_POINTS = 1200
    MAX_NUM_PLAYERS = 40


class Subsession(BaseSubsession):

    def creating_session(self):
        if self.round_number == 1:
            group = self.get_groups()[0]
            group.set_game_over(False)


class Group(BaseGroup):

    no_share_counts = models.IntegerField(initial=0)

    def get_num_players(self):
        return len(self.get_players())

    def get_no_share_counts(self):
        return self.no_share_counts

    def set_game_over(self, game_over):
        self.session.vars['game_2_over'] = game_over

    def set_first_time_game_over(self, first_time_game_over):
        self.session.vars['first_time_game_over'] = first_time_game_over

    def is_game_over(self):
        return self.session.vars['game_2_over']

    def is_first_time_game_over(self):
        return self.session.vars['first_time_game_over']

    def set_no_share_counts(self, counts):
        self.no_share_counts = counts

    def variance_subject_account(self):
        players_points_list = []
        for player in self.get_players():  # get.players is a function from otree
            players_points_list.append(player.get_points())
        return statistics.variance(players_points_list)

    def set_total_points_average(self, points_average):
        self.session.vars['total_points_average'] = points_average

    def get_total_points_average(self):
        return self.session.vars['total_points_average']

    def save_players_points(self, players, save_type):
        for p in players:
            if save_type == 'origin_amount':
                p.set_origin_amount(p.get_points())
            elif save_type == 'total_amount':
                p.set_total_amount(p.get_points())

    def set_players_points(self, players):
        for sent_player in players:
            sent_amount_list = sent_player.get_sent_amount_list()
            for rcv_player_id in range(1, self.get_num_players() + 1):
                if rcv_player_id != sent_player.get_id():
                    rcv_player = self.get_player_by_id(rcv_player_id)
                    rcv_player.set_receive_amount(rcv_player.get_receive_amount() + sent_amount_list[rcv_player_id])
                    rcv_player.set_points(rcv_player.get_points() + sent_amount_list[rcv_player_id])
            sent_player.set_sent_total_amount(sum(sent_amount_list))
            if sent_player.get_sent_total_amount() == 0:
                self.set_no_share_counts(self.get_no_share_counts() + 1)
            sent_player.set_points(sent_player.get_points() - sent_player.get_sent_total_amount())

    def confirm_game_over(self):
        if self.variance_subject_account() < 1:
            self.set_game_over(game_over=True)
            self.set_first_time_game_over(first_time_game_over=True)
            self.set_all_players_payoff()

    def set_points(self):
        players = self.get_players()
        self.save_players_points(players, save_type='origin_amount')
        self.set_players_points(players)
        self.save_players_points(players, save_type='total_amount')

    def set_all_players_payoff(self):
        finalRound = self.round_number
        groupReward = list(range(350, 50, -int(math.floor(300 / finalRound))))
        points = groupReward[finalRound - 1]

        # assign the reward to participants
        for player in self.get_players():
            player.participant.payoff += points


def player_make_field():
    return models.IntegerField(initial=0, blank=True)


class Player(BasePlayer):

    origin_amount = models.IntegerField()
    total_amount = models.IntegerField()
    sent_total_amount = models.IntegerField()
    receive_amount = models.IntegerField(initial=0)

    for i in range(1, Constants.MAX_NUM_PLAYERS + 1):
        locals()["sent_amount_%s" % i] = player_make_field()
    del i

    def get_id(self):
        return self.id_in_group

    def get_points(self):
        return self.participant.vars['points']

    def get_origin_amount(self):
        return self.origin_amount

    def get_sent_total_amount(self):
        return self.sent_total_amount

    def get_receive_amount(self):
        return self.receive_amount

    def get_total_amount(self):
        return self.total_amount

    # return the list of sent amount which the player sents to other players
    def get_sent_amount_list(self):
        num_players = self.group.get_num_players()
        sent_amount_list = [0] * (num_players + 1)
        for i in range(1, num_players + 1):
            if self.get_id() != i:
                sent_amount_list[i] = getattr(self, 'sent_amount_%s' % i)
        return sent_amount_list

    def get_points_choices(self):
        choices = []
        for currency in range(0, self.get_points() + 1):
            choices.append(currency)
        return choices

    def set_points(self, points):
        self.participant.vars['points'] = points

    def set_origin_amount(self, amount):
        self.origin_amount = amount

    def set_sent_total_amount(self, amount):
        self.sent_total_amount = amount

    def set_receive_amount(self, amount):
        self.receive_amount = amount

    def set_total_amount(self, amount):
        self.total_amount = amount

    def _get_points_choices(self):
        return self.get_points_choices()

    for i in range(1, Constants.MAX_NUM_PLAYERS + 1):
        locals()["sent_amount_%s_choices" % i] = types.FunctionType(_get_points_choices.__code__, {})
    del i













