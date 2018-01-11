# This file is part of activity module for Tryton. The COPYRIGHT file at
# the top level of this repository contains the full copyright notices and
# license terms.
try:
    from trytond.modules.activity.tests.test_activity import suite
except ImportError:
    from .test_activity import suite

__all__ = ['suite']
