from . import pages
from ._builtin import Bot


class PlayerBot(Bot):

    def play_round(self):
        if self.round_number == 1:

            print(self.player.get_points())

            if self.player.get_id == 1:
                yield (pages.Send, {'sent_amount_2': 10,
                                    'sent_amount_3': 40})
            elif self.player.get_id == 2:
                yield (pages.Send, {'sent_amount_1': 5,
                                    'sent_amount_3': 20})
            elif self.player.get_id == 3:
                yield (pages.Send, {'sent_amount_1': 60,
                                    'sent_amount_2': 20})

            yield (pages.Results)

        else:
            if self.player.get_id == 1:
                yield (pages.Send, {'sent_amount_2': 0,
                                    'sent_amount_3': 0})
            elif self.player.get_id == 2:
                yield (pages.Send, {'sent_amount_1': 0,
                                    'sent_amount_3': 0})
            elif self.player.get_id == 3:
                yield (pages.Send, {'sent_amount_1': 0,
                                    'sent_amount_2': 0})

            yield (pages.Results)



