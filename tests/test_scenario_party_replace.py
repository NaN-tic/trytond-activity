import datetime
import unittest

from proteus import Model, Wizard
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules, set_user


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install activity
        config = activate_modules('activity')

        # Create company
        _ = create_company()
        company = get_company()

        # Create a party
        Party = Model.get('party.party')
        party = Party(name='Pam')
        _ = party.identifiers.new(code="Identifier", type=None)
        _ = party.contact_mechanisms.new(type='other', value="mechanism")
        party.save()
        address, = party.addresses
        address.street = "St sample, 15"
        address.city = "City"
        address.save()

        # Create a party2
        party2 = Party(name='Pam')
        _ = party2.identifiers.new(code="Identifier2", type=None)
        _ = party2.contact_mechanisms.new(type='other', value="mechanism")
        party2.save()
        address2, = party2.addresses
        address2.street = "St sample 2, 15"
        address2.city = "City 2"
        address2.save()

        # Create employee
        Employee = Model.get('company.employee')
        eparty = Party(name='Employee')
        eparty.save()
        employee = Employee()
        employee.party = eparty
        employee.company = company
        employee.save()
        employee1 = Employee()
        employee1.party = eparty
        employee1.company = company
        employee1.save()

        # Set user
        User = Model.get('res.user')
        user = User(config.user)
        user.employees.append(Employee(employee.id))
        user.employee = employee
        user.save()
        set_user(user)

        # Create activities
        Activity = Model.get('activity.activity')
        ActivityType = Model.get('activity.type')
        activity_type, = ActivityType.find([], limit=1)
        for empl in (employee, employee, employee1):
            activity = Activity()
            activity.party = party
            activity.employee = empl
            activity.activity_type = activity_type
            activity.dtstart = datetime.datetime.now()
            activity.save()

        self.assertEqual(len(Activity.find([])), 3)
        self.assertEqual(len(Activity.find([('mine', '=', True)])), 2)
        self.assertEqual(len(Activity.find([('mine', '=', False)])), 1)
        self.assertEqual(len(Activity.find([('mine', '!=', True)])), 1)
        self.assertEqual(len(Activity.find([('mine', '!=', False)])), 2)
        # Try replace active party
        replace = Wizard('party.replace', models=[party])
        replace.form.source = party
        replace.form.destination = party2
        replace.execute('replace')

        # Check fields have been replaced
        activity.reload()
        self.assertEqual(activity.party, party2)
