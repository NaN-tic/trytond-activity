from trytond.model import fields
from trytond.pool import PoolMeta


class Employee(metaclass=PoolMeta):
    __name__ = 'company.employee'
    color = fields.Char('Color')
