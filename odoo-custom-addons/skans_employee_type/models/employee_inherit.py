from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    employee_type_2 = fields.Selection([
        ('school', 'School'),
        ('college', 'College'),
    ],string="Employee Type", default=False, track_visibility='always', store=True)
