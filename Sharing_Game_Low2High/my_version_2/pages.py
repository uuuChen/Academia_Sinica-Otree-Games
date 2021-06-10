from ._builtin import Page, WaitPage
from .models import Constants
import types


class Send(Page):

    form_model = 'player'

    timeout_seconds = 60

    def get_points_choices(self):
        return self.player.get_points_choices()

    # create "sent_amount_[1 - max_num_players]_choices" functions that call get_points_choices
    for i in range(1, Constants.MAX_NUM_PLAYERS + 1):
        locals()["sent_amount_%s_choices" % i] = types.FunctionType(get_points_choices.__code__, {})
    del i

    def get_form_fields(self):
        form_fields = ['sent_amount_{}'.format(i) for i in range(1, self.group.get_num_players() + 1)]
        del form_fields[self.player.get_id() - 1]
        return form_fields


    def vars_for_template(self):
        return {
            'player_id': self.player.get_id(),
            'player_get_points': self.player.get_points(),
            'players': self.group.get_players(),
            'receive_players_id': self.receive_players_id_choices(),
        }

    def receive_players_id_choices(self):
        receive_players_id = []
        for id in range(1, self.group.get_num_players() + 1):
            if self.player.get_id() != id:
                receive_players_id.append(str(id))
        return receive_players_id

    def error_message(self, values):
        values_sum = 0
        for key in values:
            if values[key] == None:
                values[key] = 0
            values_sum += values[key]

        if values_sum > self.player.get_points():
            return '您可以給的點數最高為 ' + str(self.player.get_points()) + ' 點 '

class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_points()
        self.group.confirm_game_over()


class Results(Page):

    def vars_for_template(self):
        return {
            'player_in_all_rounds': self.player.in_all_rounds(),
            'players': self.group.get_players(),
            'player_id': [i for i in range(1, self.group.get_num_players() + 1)],
        }


class ResultSummary(Page):

    def is_displayed(self):
        return self.group.game_over

    def vars_for_template(self):
        return {
            'player_in_all_rounds': self.player.in_all_rounds(),
            'players': self.group.get_players(),
            'player_id': [i for i in range(1, self.group.get_num_players() + 1)],
        }


page_sequence = [
    Send,
    ResultsWaitPage,
    Results,
    ResultSummary,
]
