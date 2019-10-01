# This file is part of activity module for Tryton. The COPYRIGHT file at
# the top level of this repository contains the full copyright notices and
# license terms.
from trytond.pool import Pool
from . import configuration
from . import activity
from . import party
from . import employee


def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationSequence,
        activity.ActivityType,
        activity.ActivityReference,
        activity.Activity,
        activity.ActivityCalendarContext,
        party.Party,
        employee.Employee,
        module='activity', type_='model')
    Pool.register(
        party.PartyReplace,
        module='activity', type_='wizard')
