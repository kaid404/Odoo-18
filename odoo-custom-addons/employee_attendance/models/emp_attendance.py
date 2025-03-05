from odoo import models, fields, api


class employee_attendance(models.Model):
    _inherit = 'hr.employee'

    attendances = fields.One2many('hr.attendance', 'employee_id', string="Attendances")
    contracts = fields.One2many('hr.contract', 'employee_id', string="Contracts")
    # attendance_count = fields.Integer(string="Attendance Count")
    # check_in = fields.Datetime(string="Check In", compute='_compute_get_attendances')
    # check_out = fields.Datetime(string="Check Out", compute='_compute_get_attendances')
    # worked_hours = fields.Float(string="Worked Hours", compute='_compute_get_attendances')
    # overtime_hours = fields.Float(string="Overtime Hours", compute='_compute_get_attendances')
    # # overtime_status = fields.Selection(string="Overtime Status", compute='_compute_get_attendances')
    # validated_overtime_hours = fields.Float(string="Validated Overtime Hours", compute='_compute_get_attendances')



    # def _compute_get_attendances(self):
    #     for record in self:
    #         attendances = self.env['hr.attendance'].search_read([('employee_id', '=', record.id)])
    #         for att in attendances:
    #             record.check_in = att['check_in']
    #             record.check_out = att['check_out']
    #             record.worked_hours = att['worked_hours']
    #             record.overtime_hours = att['overtime_hours']
    #             record.validated_overtime_hours = att['validated_overtime_hours']
    #
    #         print(attendances)




