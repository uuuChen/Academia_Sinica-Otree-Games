from ._builtin import Page, WaitPage
from .models import Constants
import types
import math


class Consent(Page):

    form_model = 'player'
    form_fields = ['consent']

    def is_displayed(self):
        return self.round_number == 1

    def error_message(self, values):
        if not values['consent']:
            return '必須同意才可以進行遊戲！'


class Consent_WaitPage(WaitPage):
    def after_all_players_arrive(self):
        pass


class Pretest(Page):

    form_model = 'player'

    def is_displayed(self):
        return self.round_number == 1

    def get_form_fields(self):
        form_fields = []
        for i in range(1, Constants.PRETEST_QUESTION_NUMS + 1):
            form_fields.append('pretest_{}_options'.format(i))
        return form_fields

    def get_options_choices(self):
        return [
            ['A', '2 點'],
            ['B', '6 點'],
            ['C', '0 點'],
            ['D', '4 點'],
        ]

    for i in range(1, 4 + 1):
        locals()['pretest_{}_options_choices'.format(i)] = types.FunctionType(get_options_choices.__code__, {})
    del i

    def pretest_5_options_choices(self):
        return [
            ['A', '剛好 2 個'],
            ['B', '最多 2 個']
        ]

    def error_message(self, values):
        error_ques_idxs = []
        for i in range(1, Constants.PRETEST_QUESTION_NUMS + 1):
            user_answer = values['pretest_{}_options'.format(i)]
            corr_answer = Constants.PRETEST_ANSWERS[i-1]
            if user_answer != corr_answer:
                error_ques_idxs.append(i)
        if len(error_ques_idxs) != 0:
            error_ques_idxs_str = ''
            for idx in error_ques_idxs:
                error_ques_idxs_str += ('(%s) ' % idx)
            return '問題 ' + error_ques_idxs_str + '答錯了！'


class Pretest_WaitPage(WaitPage):
    def after_all_players_arrive(self):
        pass


class Stage_1(Page):

    form_model = 'player'
    # timeout_seconds = 60

    def vars_for_template(self):
        return {
            'cur_id': self.player.get_id(),
            'cur_records': self.player.get_stage_1_self_records(),
            'has_any_connection': self.player.has_any_connection(),
            'given_records': self.player.get_stage_1_conn_others_records(given=True),
            'non_given_records': self.player.get_stage_1_conn_others_records(given=False),
            'is_game_over': self.player.is_game_over(),
            'round_number': self.round_number,
        }

    def get_form_fields(self):
        if self.player.has_any_connection() or self.round_number == 1:
            return ['coop_with_others']
        else:
            return []

    def coop_with_others_choices(self):
        return [
            [True, '給'],
            [False, '不給']
        ]


class Stage_1_WaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.compute_points_by_stage_1_results()
        self.group.plot_stage1Results2jpg(self.group.get_players())


class Stage_1_Results(Page):

    def vars_for_template(self):
        return {
            'cur_id': self.player.get_id(),
            'cur_records': self.player.get_stage_1_self_records(),
            'given_records': self.player.get_stage_1_conn_others_records(given=True),
            'non_given_records': self.player.get_stage_1_conn_others_records(given=False),
            'round_number': self.round_number,
        }

    def is_displayed(self):
        return not self.player.is_game_over() or self.player.is_first_time_game_over()


class Stage_2(Page):

    form_model = 'player'
    # timeout_seconds = 60

    def get_form_fields(self):
        form_fields = []
        for other_player in self.player.get_others_in_group():
            form_fields.append('cut_{}'.format(other_player.get_id()))
        return form_fields

    def vars_for_template(self):
        return {
            'cur_id': self.player.get_id(),
            'others_records':  self.player.get_stage_2_conn_others_records(),
            'has_any_connection': self.player.has_any_connection(),
            'round_number': self.round_number,
        }

    # def js_vars(self):
    #     return dict(
    #         payoff=self.player.payoff,
    #         cur_id=self.player.get_id(),
    #         highcharts_data=[
    #           ['Node 1', 'Node 2'],
    #           ['Node 1', 'Node 3'],
    #           ['Node 1', 'Node 4'],
    #           ['Node 1', 'Node 5'],
    #         ],
    #     )


class Stage_2_WaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.make_groups_by_stage_2_results()
        self.group.check_whether_is_game_over()


class Stage_2_Results(Page):

    def vars_for_template(self):
        return {
            'cur_id': self.player.get_id(),
            'cur_records': self.player.get_stage_2_results_self_records(),
            'round_number': self.round_number,
        }

    def is_displayed(self):
        return not self.player.is_game_over() or self.player.is_first_time_game_over()

    def before_next_page(self):
        if self.player.is_first_time_game_over():
            self.player.set_is_first_time_game_over(False)


class Plot_Results(Page):

    def is_displayed(self):
        return self.group.get_are_all_game_over()


class All_Game_Over_1(Page):

    def vars_for_template(self):
        return {
            'cur_id': self.player.get_id(),
            'payoff': math.ceil(self.player.get_total_points()),
        }

    def is_displayed(self):
        return self.group.get_are_all_game_over()


class Questionnaire(Page):

    form_model = 'player'

    def get_form_fields(self):
        form_fields = []
        for i in range(1, Constants.QUESTIONNAIRE_QUESTION_NUMS + 1):
            form_fields.append('questionnaire_{}_options'.format(i))
        return form_fields

    def is_displayed(self):
        return self.group.get_are_all_game_over()


class All_Game_Over_2(Page):

    def vars_for_template(self):
        return {
            'cur_id': self.player.get_id(),
            'payoff': math.ceil(self.player.get_total_points()),
        }

    def is_displayed(self):
        return self.group.get_are_all_game_over()


page_sequence = [
    # Consent,
    # Consent_WaitPage,
    # Pretest,
    # Pretest_WaitPage,
    Stage_1,
    Stage_1_WaitPage,
    Stage_1_Results,
    Stage_2,
    Stage_2_WaitPage,
    Stage_2_Results,
    All_Game_Over_1,
    Questionnaire,
    All_Game_Over_2,
]


