from ._builtin import Page, WaitPage
from .models import Constants
import types


class Instruction(Page):

    def is_displayed(self):
        return self.round_number == 1


class InstructionWaitPage(WaitPage):
    def after_all_players_arrive(self):
        pass

    def is_displayed(self):
        return self.round_number == 1


class Send(Page):

    form_model = 'player'

    timeout_seconds = 60

    def get_points_choices(self):
        return self.player.get_points_choices()

    for i in range(1, Constants.MAX_NUM_PLAYERS + 1):
        locals()["sent_amount_%s_choices" % i] = types.FunctionType(get_points_choices.__code__, {})
    del i

    # learn from the bottom of 'Forms'
    def get_form_fields(self):
        form_fields = ['sent_amount_{}'.format(i) for i in range(1, self.group.get_num_players() + 1)]
        del form_fields[self.player.get_id() - 1]  # delete the form_field which matches to current player him/herself
        return form_fields

    def vars_for_template(self):
        return {
            'player_id': self.player.get_id(),
            'player_get_points': self.player.get_points(),
            'players': self.group.get_players(),
            'receive_players_id': self.receive_players_id_choices(),
            'points_average': self.group.get_total_points_average(),
        }

    def receive_players_id_choices(self):
        receive_players_id = []
        for id in range(1, self.group.get_num_players() + 1):
            # receive_players don't include current player him/herself
            if self.player.get_id() != id:
                receive_players_id.append(str(id))
        return receive_players_id

    def error_message(self, values):

        values_sum = 0  # 'values' is a dict and its keys are all form_fileds

        # count total amount which current player sends to others, and it can't exceed the amount the player has
        for key in values:
            if values[key] == None:
                values[key] = 0
            values_sum += values[key]

        # if total amount exceeds the amount the player has, return error string
        if values_sum > self.player.get_points():
            return '您可以給的點數最高為 ' + str(self.player.get_points()) + ' 點 '

    def is_displayed(self):
        return not self.group.is_game_over()


class ResultsWaitPage(WaitPage):

    # each round when all players finish the decision, the program turns to here
    def after_all_players_arrive(self):
        self.group.set_points()
        self.group.confirm_game_over()

    def is_displayed(self):
        return not self.group.is_game_over() or self.group.is_first_time_game_over()


class Results(Page):

    def vars_for_template(self):
        return {
            'player_in_all_rounds': self.player.in_all_rounds(),
            'players': self.group.get_players(),
            'player_id': [i for i in range(1, self.group.get_num_players() + 1)],
        }

    def is_displayed(self):
        return not self.group.is_game_over() or self.group.is_first_time_game_over()


class ResultSummary(Page):

    def vars_for_template(self):
        return {
            'player_in_all_rounds': self.player.in_all_rounds(),
            'players': self.group.get_players(),
            'player_id': [i for i in range(1, self.group.get_num_players() + 1)],
        }

    # The page will only be displayed when return is 'True'
    def is_displayed(self):
        return self.group.is_first_time_game_over()


class ResultSummaryWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.set_first_time_game_over(False)
        self.group.set_all_players_payoff()
        total_points = self.subsession.init_players_points('high')
        self.group.set_total_points_average(float(total_points / self.group.get_num_players()))

    def is_displayed(self):
        return self.group.is_first_time_game_over()


page_sequence = [
    Instruction,
    InstructionWaitPage,
    Send,
    ResultsWaitPage,
    Results,
    ResultSummary,
    ResultSummaryWaitPage,
]
