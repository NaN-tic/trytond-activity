======================
Party Replace Scenario
======================

Imports::

    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company

Install activity::

    >>> config = activate_modules('activity')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create a party::

    >>> Party = Model.get('party.party')
    >>> party = Party(name='Pam')
    >>> _ = party.identifiers.new(code="Identifier", type=None)
    >>> _ = party.contact_mechanisms.new(type='other', value="mechanism")
    >>> party.save()
    >>> address, = party.addresses
    >>> address.street = "St sample, 15"
    >>> address.city = "City"
    >>> address.save()

Create a party2::

    >>> party2 = Party(name='Pam')
    >>> _ = party2.identifiers.new(code="Identifier2", type=None)
    >>> _ = party2.contact_mechanisms.new(type='other', value="mechanism")
    >>> party2.save()
    >>> address2, = party2.addresses
    >>> address2.street = "St sample 2, 15"
    >>> address2.city = "City 2"
    >>> address2.save()

Create employee::

    >>> Employee = Model.get('company.employee')
    >>> employee = Employee()
    >>> eparty = Party(name='Employee')
    >>> eparty.save()
    >>> employee.party = eparty
    >>> employee.company = company
    >>> employee.save()

Create activities::

    >>> Activity = Model.get('activity.activity')
    >>> IrModel = Model.get('ir.model')
    >>> ActivityType = Model.get('activity.type')
    >>> activity_type, = ActivityType.find([], limit=1)
    >>> activity = Activity()
    >>> activity.party = party
    >>> activity.employee = employee
    >>> activity.activity_type = activity_type
    >>> activity.save()

Try replace active party::

    >>> replace = Wizard('party.replace', models=[party])
    >>> replace.form.source = party
    >>> replace.form.destination = party2
    >>> replace.execute('replace')

Check fields have been replaced::

    >>> activity.reload()
    >>> activity.party == party2
    True
