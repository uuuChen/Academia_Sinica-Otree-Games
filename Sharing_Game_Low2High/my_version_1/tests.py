from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants


class PlayerBot(Bot):

    def play_round(self):
        yield (pages.Send, {
                   'sent_amount_1' : 500,
                   'sent_amount_2': 2000,
                   'sent_amount_3': 1000,
                   'sent_amount_4': 700,
                   'sent_amount_5': 6600,
                   'sent_amount_6': 6000,
                   'sent_amount_7': 300,
                   'sent_amount_8': 5700,
                   'sent_amount_9': 900,
                   'sent_amount_10': 300,
                   'share_or_not': 'True'})

        yield (pages.Results, {

            })
