from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)
from datetime import date, datetime
from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class CampusTransfer(models.Model):
    _name = "gxs.campus.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'

    student_id = fields.Many2one('op.student', string='Student', required=True, store=True, tracking=True, copy=False)

    campus_id = fields.Many2one('gxs.campus', string='Campus', store=True, readonly=True, tracking=True, copy=False)
    new_campus_id = fields.Many2one('gxs.campus', string='New Campus', required=True, store=True, tracking=True,
                                    copy=False)
    new_class_id = fields.Many2one('op.academic.year', string='New Academic Class', store=True, copy=True)

    new_section_id = fields.Many2one('class.section', string='New Section', required=True, store=True, tracking=True,
                                     copy=False,domain="[('class_id', '=', new_class_id)]")
    reason = fields.Text(string='Reason', required=True, store=True, tracking=True, copy=False)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('refuse', 'Refused'),
            ('done', 'Done'),
        ], default='draft', string='State', store=True, tracking=True, copy=False)

    @api.onchange('student_id')
    def onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.campus_id = rec.student_id.x_camp_id

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def action_confirm(self):
        for rec in self:
            m_result_record = self.env['milestone.std.performance'].sudo().search(
                [('student_id', '=', rec.student_id.id), ('campus_id', '=', rec.campus_id.id)])
            _logger.info(m_result_record)
            _logger.info(m_result_record)
            _logger.info(m_result_record)
            for result in m_result_record:
                result.sudo().write({'campus_id': rec.new_campus_id.id})
            result_record = self.env['gxs.std.performance'].search(
                [('student_id', '=', rec.student_id.id), ('campus_id', '=', rec.campus_id.id)])
            _logger.info('resukt')
            _logger.info(result_record)
            for result in result_record:
                result.sudo().write({'campus_id': rec.new_campus_id.id})

            rec.student_id.is_transfer = True
            rec.student_id.x_camp_id = rec.new_campus_id.id
            rec.student_id.sudo().user_id.gxs_campus_id = rec.new_campus_id.ids
            rec.student_id.sudo().user_id.company_ids = rec.student_id.sudo().user_id.company_ids.ids + rec.new_campus_id.company_id.ids
            rec.student_id.sudo().user_id.company_id = rec.new_campus_id.company_id.id

            reg_ids = self.env['op.student.course'].search(
                [('student_id', '=', self.student_id.id), ('academic_years_id', '=', self.student_id.year_id.id)])
            for std_reg in reg_ids:
                std_reg.unlink()

            new_course = self.env['op.course'].search([('class_id', '=', self.new_class_id.id)], limit=1).id
            if not new_course:
                raise UserError('No course available for %s ' % self.new_class_id.name)

            registered = self.env['op.subject.registration'].create({
                'student_id': self.student_id.id,
                'course_id': new_course,
                'class_id': self.new_class_id.id,
            })
            registered.get_subjects()
            registered.action_submitted()
            registered.action_approve()





            old_sections = self.env['class.section'].sudo().search([
                ('students', 'in', rec.student_id.id),
                ('id', '!=', rec.new_section_id.id),
            ])

            for section in old_sections:
                section.students = [(3, rec.student_id.id)]



    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("You cannot delete a record that is in the Done state."))
        return super(CampusTransfer, self).unlink()

    # company_id = fields.Many2one(
    #     'res.company', string='Campus',
    #     default=lambda self: self.env.user.company_id)

    # def _default_students(self):
    #     active_ids = self.env.context.get('active_ids')
    #
    #     print(active_ids)
    #     return active_ids
    # return self.env['op.student'].search([('active', '=', True)])

    # def transfer(self):
    #     for rec in self.student_ids:
    #         rec.sudo().user_id.company_ids = rec.user_id.company_ids.ids + self.company_id.ids
    #         rec.sudo().user_id.company_id = self.company_id.id
    #         print('>>>>>>>>>>>3')
    #
    #         rec.sudo().partner_id.company_id = self.company_id.id
    #
    #         print('>>>>>>>>>1')
    #         rec.sudo().company_id = self.company_id.id
    #
    #         print('>>>>>>>>>>2')
