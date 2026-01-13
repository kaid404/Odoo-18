from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)


class HREmployee(models.Model):
	_inherit = 'hr.employee'
	
	allowed_grace = fields.Boolean(string="Allowed Grace")


class ResourceCalendar(models.Model):
	_inherit = 'resource.calendar'
	
	grace_hours = fields.Float(string="Grace Hours")


class ResCompany(models.Model):
	_inherit = 'res.company'

	basic_govt_wage = fields.Float(string="Basic Govt Wage")


class HRAttendance(models.Model):
	_inherit = 'hr.attendance'
	
	@api.depends('check_in', 'check_out')
	def _compute_worked_hours(self):
		
		super(HRAttendance, self)._compute_worked_hours()
		
		for attendance in self:
			if attendance.worked_hours and attendance.employee_id:
				employee = attendance.employee_id
				shift = employee.resource_calendar_id
				if employee.allowed_grace and shift and shift.grace_hours > 0:
					attendance.worked_hours += shift.grace_hours
