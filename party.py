# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = ['Party', 'PartyReplace']


class Party(metaclass=PoolMeta):
    __name__ = "party.party"
    activities = fields.One2Many('activity.activity', 'party', 'Activities')


class PartyReplace(metaclass=PoolMeta):
    __name__ = 'party.replace'

    @classmethod
    def fields_to_replace(cls):
        return super(PartyReplace, cls).fields_to_replace() + [
            ('activity.activity', 'party'),
            ]
