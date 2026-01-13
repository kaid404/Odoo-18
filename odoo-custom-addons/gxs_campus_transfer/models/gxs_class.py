from odoo import api, fields, models, _
import logging 

_logger = logging.getLogger(__name__)
from datetime import date, datetime
from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ClassTransfer(models.Model):
    _name = "gxs.class.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'

    student_id = fields.Many2one('op.student', string='Student', required=True, store=True, tracking=True, copy=False)

    section_id = fields.Many2one('class.section', string='Section', store=True, readonly=True, tracking=True,
                                 copy=False)


    # class_id = fields.Many2one('op.academic.year', string='Academic Class',related='student_id.year_id')
    class_id = fields.Many2one('op.academic.year', string='Academic Class',readonly=True)

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
                rec.class_id = rec.student_id.year_id
            if rec.student_id:
                rec.section_id = rec.student_id.section_id

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def action_confirm(self):
        for rec in self:
            m_result_record = self.env['milestone.std.performance'].sudo().search(
                [('student_id', '=', rec.student_id.id),('class_id','=',self.class_id.id)])
            _logger.info(m_result_record)
            _logger.info(m_result_record)
            _logger.info(m_result_record)
            for result in m_result_record:
                result.sudo().unlink()
                # result.sudo().write({'section_id': rec.new_section_id.id})


            result_record = self.env['milestone.std.result'].search(
                [('student_id', '=', rec.student_id.id),('class_id','=',self.class_id.id)])
            _logger.info('resukt')
            _logger.info(result_record)
            for result in result_record:
                result.sudo().unlink()
                # result.sudo().write({'section_id': rec.new_section_id.id})

            
            result_record = self.env['gxs.std.performance'].search(
                [('student_id', '=', rec.student_id.id),('class_id','=',self.class_id.id)])
            _logger.info('resukt')
            _logger.info(result_record)
            for result in result_record:
                result.sudo().unlink()
                # result.sudo().write({'section_id': rec.new_section_id.id})

            result_record = self.env['gxs.std.result'].search(
                [('student_id', '=', rec.student_id.id),('class_id','=',self.class_id.id)])
            _logger.info('resukt')
            _logger.info(result_record)
            for result in result_record:
                result.sudo().unlink()
                # result.sudo().write({'section_id': rec.new_section_id.id})

            reg_ids = self.env['op.subject.registration'].search(
                [('student_id', '=',self.student_id.id),('class_id','=',self.class_id.id)])
            for std_reg in reg_ids:
                std_reg.action_reset_draft()
                std_reg.action_reject()
                std_reg.unlink()

            reg_ids = self.env['op.student.course'].search(
                [('student_id', '=', self.student_id.id), ('academic_years_id', '=', self.class_id.id)])
            for std_reg in reg_ids:
                std_reg.unlink()

                # std_reg.action_reset_draft()
                # std_reg.action_reject()









                
            
            rec.student_id.section_id = self.new_section_id.id
            rec.student_id.year_id = self.new_class_id.id
            self.new_section_id.students = self.new_section_id.students.ids +  self.student_id.ids

            old_sections = self.env['class.section'].sudo().search([('students','ilike',rec.student_id.id),('id','!=',rec.new_section_id.id)])
            for old_section in old_sections:
                # old_section.students = old_section.students.ids - rec.student_id.ids
                old_section.students = [(6, 0, list(set(old_section.students.ids) - set(rec.student_id.ids)))]
            rec.write({'state':'done'})

            current_course = self.env['op.course']
            registration = self.env['op.subject.registration']
            new_course = current_course.search([('class_id', '=', self.new_class_id.id)], limit=1).id
            if not new_course:
                raise UserError('No course available for %s ' % self.new_class_id.name)

            registered = registration.create({
                'student_id': self.student_id.id,
                'course_id': new_course,
                'class_id': self.new_class_id.id,
            })

            registered.get_subjects()
            registered.action_submitted()
            registered.action_approve()

            # rec.student_id.x_camp_id = rec.new_campus_id.id
            # rec.student_id.sudo().user_id.gxs_campus_id = rec.new_campus_id.ids
            # rec.student_id.sudo().user_id.company_ids = rec.student_id.sudo().user_id.company_ids.ids + rec.new_campus_id.company_id.ids
            # rec.student_id.sudo().user_id.company_id = rec.new_campus_id.company_id.id

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("You cannot delete a record that is in the Done state."))
        return super(ClassTransfer, self).unlink()

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
