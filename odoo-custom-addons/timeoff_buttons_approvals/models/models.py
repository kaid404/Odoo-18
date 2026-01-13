from odoo import models, fields, api


class TimeoffApprovals(models.Model):
    _inherit = 'hr.leave'
#
    state = fields.Selection([
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Line Manager Approved'),
        ('validate', 'HR Approved'),
        ('cancel', 'Cancelled'),
    ], string='Status', store=True, tracking=True, copy=False, readonly=False, default='confirm',
        help="The status is set to 'To Submit', when a time off request is created." +
             "\nThe status is 'To Approve', when time off request is confirmed by user." +
             "\nThe status is 'Refused', when time off request is refused by manager." +
             "\nThe status is 'Approved', when time off request is approved by manager.")
