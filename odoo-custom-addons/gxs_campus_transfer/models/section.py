from odoo import api, fields, models, _
import logging 

_logger = logging.getLogger(__name__)
from datetime import date, datetime
from datetime import timedelta
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class SectionTransfer(models.Model):
    _name = "gxs.section.transfer"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'

    student_id = fields.Many2one('op.student', string='Student', required=True, store=True, tracking=True, copy=False)

    section_id = fields.Many2one('class.section', string='Section', store=True, readonly=True, tracking=True,
                                 copy=False)


    class_id = fields.Many2one('op.academic.year', string='Academic Class', store=True, copy=True,related='section_id.class_id')

    new_section_id = fields.Many2one('class.section', string='New Section', required=True, store=True, tracking=True,
                                     copy=False,domain="[('class_id', '=', class_id)]")
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
                [('student_id', '=', rec.student_id.id),('section_id','=',self.section_id.id)])
            _logger.info(m_result_record)
            _logger.info(m_result_record)
            _logger.info(m_result_record)
            for result in m_result_record:
                result.sudo().write({'section_id': rec.new_section_id.id})


            result_record = self.env['milestone.std.result'].search(
                [('student_id', '=', rec.student_id.id),('section_id','=',self.section_id.id)])
            _logger.info('resukt')
            _logger.info(result_record)
            for result in result_record:
                result.sudo().write({'section_id': rec.new_section_id.id})

            
            result_record = self.env['gxs.std.performance'].search(
                [('student_id', '=', rec.student_id.id),('section_id','=',self.section_id.id)])
            _logger.info('resukt')
            _logger.info(result_record)
            for result in result_record:
                result.sudo().write({'section_id': rec.new_section_id.id})

            result_record = self.env['gxs.std.result'].search(
                [('student_id', '=', rec.student_id.id),('section_id','=',self.section_id.id)])
            _logger.info('resukt')
            _logger.info(result_record)
            for result in result_record:
                result.sudo().write({'section_id': rec.new_section_id.id})
                
            
            rec.student_id.section_id = self.new_section_id.id
            self.new_section_id.students = self.new_section_id.students.ids +  self.student_id.ids

            old_sections = self.env['class.section'].sudo().search([('students','ilike',rec.student_id.id),('id','!=',rec.new_section_id.id)])
            for old_section in old_sections:
                # old_section.students = old_section.students.ids - rec.student_id.ids
                old_section.students = [(6, 0, list(set(old_section.students.ids) - set(rec.student_id.ids)))]
            rec.write({'state':'done'})


    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("You cannot delete a record that is in the Done state."))
        return super(SectionTransfer, self).unlink()


class SectionTransferBulk(models.Model):
    _name = "gxs.section.transfer.bulk"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'student_id'



    section_id = fields.Many2one('class.section', string='Section', store=True, readonly=True, tracking=True,
                                 copy=False)

    class_id = fields.Many2one('op.academic.year', string='Academic Class', store=True, copy=True,)

    new_section_id = fields.Many2one('class.section', string='New Section', required=True, store=True, tracking=True,
                                     copy=False, domain="[('class_id', '=', class_id)]")
    student_ids = fields.Many2many('op.student', string='Student', required=True,  tracking=True)
    # student_ids = fields.Many2many('op.student', string='Student', required=True,  tracking=True,domain="[('year_id', '=', class_id)]")

    reason = fields.Text(string='Reason', required=True, store=True, tracking=True, copy=False)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('refuse', 'Refused'),
            ('done', 'Done'),
        ], default='draft', string='State', store=True, tracking=True, copy=False)

    # @api.onchange('student_id')
    # def onchange_student_id(self):
    #     for rec in self:
    #         if rec.student_id:
    #             rec.section_id = rec.student_id.section_id

    def action_reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    def action_confirm(self):
        for rec in self:
            for student_id in rec.student_ids:
                m_result_record = self.env['milestone.std.performance'].sudo().search(
                    [('student_id', '=', student_id.id), ('section_id', '=', student_id.section_id.id)])
                _logger.info(m_result_record)
                _logger.info(m_result_record)
                _logger.info(m_result_record)
                for result in m_result_record:
                    result.sudo().write({'section_id': rec.new_section_id.id})

                result_record = self.env['milestone.std.result'].search(
                    [('student_id', '=', student_id.id), ('section_id', '=', student_id.section_id.id)])
                _logger.info('resukt')
                _logger.info(result_record)
                for result in result_record:
                    result.sudo().write({'section_id': rec.new_section_id.id})

                result_record = self.env['gxs.std.performance'].search(
                    [('student_id', '=', student_id.id), ('section_id', '=', student_id.section_id.id)])
                _logger.info('resukt')
                _logger.info(result_record)
                for result in result_record:
                    result.sudo().write({'section_id': rec.new_section_id.id})

                result_record = self.env['gxs.std.result'].search(
                    [('student_id', '=', student_id.id), ('section_id', '=', student_id.section_id.id)])
                _logger.info('resukt')
                _logger.info(result_record)
                for result in result_record:
                    result.sudo().write({'section_id': rec.new_section_id.id})

                student_id.section_id = self.new_section_id.id
                self.new_section_id.students = self.new_section_id.students.ids + student_id.ids

                old_sections = self.env['class.section'].sudo().search(
                    [('students', 'ilike', student_id.id), ('id', '!=', rec.new_section_id.id)])
                for old_section in old_sections:
                    # old_section.students = old_section.students.ids - rec.student_id.ids
                    old_section.students = [(6, 0, list(set(old_section.students.ids) - set(student_id.ids)))]
                rec.write({'state': 'done'})

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_("You cannot delete a record that is in the Done state."))
        return super(SectionTransfer, self).unlink()

