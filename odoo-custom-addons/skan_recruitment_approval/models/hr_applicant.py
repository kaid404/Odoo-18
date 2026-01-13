from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    institute_type = fields.Selection([
        ('school', 'School'),
        ('college', 'College'),
        ('ho', 'Head Office')
    ], string='Employment Type')

    stage_id = fields.Many2one(
        'hr.recruitment.stage',
        string='Stage',
        default=lambda self: self.env['hr.recruitment.stage'].search([('name', '=', 'New')], limit=1)
    )

    show_dynamic_button = fields.Boolean(compute='_compute_show_dynamic_button', store=True)
    dynamic_button_label = fields.Char(compute='_compute_show_dynamic_button', store=False)
    first_approved = fields.Boolean(string="First Approved")

    def create_employee_from_applicant(self):
        res = super().create_employee_from_applicant()

        for applicant in self:
            employee = self.env['hr.employee'].search(
                [('job_id', '=', applicant.job_id.id), ('name', '=', applicant.partner_name)], limit=1)

            if applicant.institute_type and employee:
                employee.employee_type_2 = applicant.institute_type

        return res

    @api.depends('stage_id', 'institute_type')
    def _compute_show_dynamic_button(self):
        for rec in self:
            rec.show_dynamic_button = False
            rec.dynamic_button_label = ''

            stage = rec.stage_id.name if rec.stage_id else 'New'

            if stage == 'New':
                rec.dynamic_button_label = 'HR Interview'
                rec.show_dynamic_button = True
            elif stage == 'HR Manager':
                rec.dynamic_button_label = 'Line Manager Interview'
                rec.show_dynamic_button = True
            elif stage == 'Line Manager':
                if rec.institute_type == 'school':
                    rec.dynamic_button_label = 'CEO Interview'
                    rec.show_dynamic_button = True
                elif rec.institute_type == 'college':
                    rec.dynamic_button_label = 'Executive Director Interview'
                    rec.show_dynamic_button = True
            elif stage in ['CEO Interview', 'Executive Director Interview']:
                rec.dynamic_button_label = 'Approved'
                rec.show_dynamic_button = True
            elif stage == 'Hired':
                rec.show_dynamic_button = False

    def action_approve_next_stage(self):
        for rec in self:
            next_stage_name = None
            stage = rec.stage_id.name if rec.stage_id else 'New'

            if stage == 'New':
                next_stage_name = 'HR Manager'
                rec.first_approved = True
            elif stage == 'HR Manager':
                next_stage_name = 'Line Manager'
            elif stage == 'Line Manager':
                if rec.institute_type == 'school':
                    next_stage_name = 'CEO Interview'
                elif rec.institute_type == 'college':
                    next_stage_name = 'Executive Director Interview'
            elif stage in ['CEO Interview', 'Executive Director Interview']:
                next_stage_name = 'Approved'

            if next_stage_name:
                next_stage = self.env['hr.recruitment.stage'].search([('name', '=', next_stage_name)], limit=1)
                if next_stage:
                    rec.stage_id = next_stage.id

            if rec.stage_id.name == 'New':
                rec.first_approved = False

    @api.onchange('stage_id')
    def _onchange_stage_id_reset_first_approved(self):
        for rec in self:
            if rec.stage_id and rec.stage_id.name == 'New':
                rec.first_approved = False

    def toggle_active(self):
        res = super().toggle_active()
        for rec in self:
            rec.first_approved = False
        return res
