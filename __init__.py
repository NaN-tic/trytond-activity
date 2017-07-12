# This file is part of activity module for Tryton. The COPYRIGHT file at
# the top level of this repository contains the full copyright notices and
# license terms.
from trytond.pool import Pool
from . import configuration
from .activity import *
from .party import *


def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationSequence,
        ActivityType,
        ActivityReference,
        Activity,
        Party,
        module='activity', type_='model')
    Pool.register(
        PartyReplace,
        module='carrier', type_='wizard')
