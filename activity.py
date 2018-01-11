# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import datetime

from sql import Null

from trytond.model import ModelSQL, ModelView, fields, sequence_ordered
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond import backend

__all__ = ['ActivityType', 'ActivityReference', 'Activity']


class ActivityType(sequence_ordered(), ModelSQL, ModelView):
    'Activity Type'
    __name__ = "activity.type"
    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active')

    @staticmethod
    def default_active():
        return True


class ActivityReference(ModelSQL, ModelView):
    'Activity Reference'
    __name__ = "activity.reference"

    model = fields.Many2One('ir.model', 'Model', required=True)


class Activity(ModelSQL, ModelView):
    'Activity'
    __name__ = "activity.activity"

    code = fields.Char('Code', readonly=True, select=True)
    activity_type = fields.Many2One('activity.type', 'Type', required=True)

    subject = fields.Char('Subject')
    resource = fields.Reference('Resource', selection='get_resource')
    dtstart = fields.DateTime('Start Date', required=True, select=True)
    dtend = fields.DateTime('End Date', select=True)
    state = fields.Selection([
            ('planned', 'Planned'),
            ('held', 'Held'),
            ('not_held', 'Not Held'),
            ], 'State', required=True)
    description = fields.Text('Description')
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    location = fields.Char('Location')
    party = fields.Many2One('party.party', 'Party')

    @classmethod
    def __setup__(cls):
        super(Activity, cls).__setup__()
        cls._order.insert(0, ('dtstart', 'DESC'))
        cls._order.insert(1, ('subject', 'DESC'))
        cls._error_messages.update({
                'no_activity_sequence': ('There is no activity sequence '
                    'defined. Please define on in activity configuration.')
                })

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        cursor = Transaction().connection.cursor()
        sql_table = cls.__table__()

        code_exists = True
        if TableHandler.table_exist(cls._table):
            table = TableHandler(cls, module_name)
            code_exists = table.column_exist('code')

        super(Activity, cls).__register__(module_name)

        table = TableHandler(cls, module_name)
        # Migration from 3.2: Remove type and direction fields
        table.not_null_action('type', action='remove')
        table.not_null_action('direction', action='remove')

        # Migration from 3.2: Add code field
        if (not code_exists and table.column_exist('type') and
                table.column_exist('direction')):
            cursor.execute(*sql_table.update(
                    columns=[sql_table.code],
                    values=[sql_table.id],
                    where=sql_table.code == Null))
            table.not_null_action('code', action='add')

        # Migration from 3.4.1: subject is no more required
        table.not_null_action('subject', 'remove')

    @fields.depends('resource', 'party')
    def on_change_with_party(self, name=None):
        if self.resource and self.resource.id > 0:
            return Activity._resource_party(self.resource)
        return self.party.id if self.party else None

    def get_rec_name(self, name):
        if self.subject:
            return '[%s] %s' % (self.code, self.subject)
        return self.code

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('code',) + tuple(clause[1:]),
            ('subject',) + tuple(clause[1:]),
            ]

    @staticmethod
    def default_dtstart():
        return datetime.datetime.now()

    @staticmethod
    def default_employee():
        User = Pool().get('res.user')
        user = User(Transaction().user)
        return user.employee and user.employee.id or None

    @staticmethod
    def default_state():
        return 'planned'

    @staticmethod
    def default_resource():
        return ''

    @classmethod
    def default_party(cls):
        resource = cls.default_resource()
        return Activity._resource_party(resource)

    @staticmethod
    def _resource_party(resource):
        if not resource or resource.id < 0:
            return

        model = resource and str(resource).partition(',')[0]
        Relation = Pool().get(model)
        if model == 'party.party':
            return resource.id
        if 'party' in Relation._fields.keys():
            if resource.party:
                return resource.party.id
        return None

    @classmethod
    def get_resource(cls):
        'Return list of Model names for resource Reference'
        ActivityType = Pool().get('activity.reference')
        res = [('', '')]
        for _type in ActivityType.search([]):
            res.append((_type.model.model, _type.model.name))
        return res

    @classmethod
    def create(cls, vlist):
        pool = Pool()
        Sequence = pool.get('ir.sequence')
        Config = pool.get('activity.configuration')

        sequence = Config(1).activity_sequence
        if not sequence:
            cls.raise_user_error('no_activity_sequence')
        vlist = [x.copy() for x in vlist]
        for vals in vlist:
            vals['code'] = Sequence.get_id(sequence.id)
        return super(Activity, cls).create(vlist)
