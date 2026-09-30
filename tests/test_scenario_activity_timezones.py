import datetime
import unittest

from proteus import Model
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.pool import Pool
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules, set_user
from trytond.transaction import Transaction


class TestActivityTimezones(unittest.TestCase):
    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):
        config = activate_modules('activity')
        create_company()
        company = get_company()
        company.timezone = 'Europe/Madrid'
        company.save()
        Party = Model.get('party.party')
        Employee = Model.get('company.employee')
        User = Model.get('res.user')
        Activity = Model.get('activity.activity')
        Type = Model.get('activity.type')
        person = Party(name='Employee')
        person.save()
        employee = Employee(party=person, company=company)
        employee.save()
        user = User(config.user)
        user.employees.append(employee)
        user.employee = employee
        user.save()
        set_user(user)
        kind = Type(name='Test')
        kind.save()
        cases = [
            (datetime.datetime(2026, 9, 30, 7, 47, 43),
                datetime.datetime(2026, 9, 30, 9, 47, 43)),
            (datetime.datetime(2026, 9, 30, 8, 29, 34),
                datetime.datetime(2026, 9, 30, 10, 29, 34)),
            (datetime.datetime(2026, 9, 29, 22, 30),
                datetime.datetime(2026, 9, 30, 0, 30)),
            (datetime.datetime(2026, 3, 29, 1, 30),
                datetime.datetime(2026, 3, 29, 3, 30)),
            (datetime.datetime(2026, 10, 25, 0, 30),
                datetime.datetime(2026, 10, 25, 2, 30)),
            (datetime.datetime(2026, 10, 25, 1, 30),
                datetime.datetime(2026, 10, 25, 2, 30)),
            ]
        for utc, local in cases:
            # Importers supply UTC, without the client's date/time on-change.
            with Transaction().start(config.database_name, config.user,
                    context=dict(config.context, company=None)) as transaction:
                ActivityModel = Pool().get('activity.activity')
                record, = ActivityModel.create([{
                            'activity_type': kind.id, 'employee': employee.id,
                            'company': company.id, 'dtstart': utc,
                            }])
                record_id = record.id
                transaction.commit()
            activity = Activity(record_id)
            self.assertEqual(activity.dtstart, utc)
            self.assertEqual(activity.date, local.date())
            self.assertEqual(activity.time, local.time())
            activity.subject = 'Unrelated change'
            activity.save()
            self.assertEqual(activity.dtstart, utc)
            activity.duration = datetime.timedelta(hours=1)
            activity.save()
            self.assertEqual(activity.dtstart, utc)
            self.assertEqual(activity.dtend, utc + datetime.timedelta(hours=1))
            activity.dtend = utc + datetime.timedelta(minutes=45)
            activity.save()
            self.assertEqual(activity.duration, datetime.timedelta(minutes=45))
            self.assertEqual(activity.dtstart, utc)

        manual = Activity(activity_type=kind, employee=employee, company=company,
            date=datetime.date(2026, 9, 30), time=datetime.time(10))
        manual.save()
        self.assertEqual(manual.dtstart, datetime.datetime(2026, 9, 30, 8))
        manual.time = None
        manual.save()
        self.assertIsNone(manual.time)
        self.assertEqual(manual.dtstart, datetime.datetime(2026, 9, 29, 22))
        manual.subject = 'All-day activity'
        manual.save()
        self.assertIsNone(manual.time)
        self.assertEqual(manual.dtstart, datetime.datetime(2026, 9, 29, 22))
