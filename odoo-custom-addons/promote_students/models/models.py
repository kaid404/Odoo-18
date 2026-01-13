from odoo import models, fields, api


class ExitInterviewForm(models.Model):
    _name = 'promote.students'

    old_batch = fields.Many2one('odoocms.batch', string="Old Batch")
    new_batch = fields.Many2one('odoocms.batch', string="New Batch")

    def promote_students(self):
        old = self.old_batch
        new = self.new_batch

        ob_students = self.env['odoocms.student'].search([('batch_id','=', old.id)])

        for student in ob_students:
            student.batch_id = new.id
            student.session_id = new.session_id.id
            student.semester_id = new.semester_id.id


        print('done')

