from odoo import models, fields, api


class GenTimeTable(models.TransientModel):
    _inherit = 'generate.time.table'

    @api.onchange('course_id')
    def _onchange_course_id(self):
        if self.course_id:
            subjects = self.course_id.subject_ids
            if subjects:
                lines = []
                for sub in subjects:
                    lines.append((0, 0, {'subject_id': sub.id, 'gen_time_table': self.id}))
                if lines:
                    self.write({'time_table_lines': lines})


class GenTimeTableLine(models.TransientModel):
    _inherit = 'gen.time.table.line'

    slot_id = fields.Many2one('op.timetable.slots', string='Slot')

    @api.onchange('slot_id', 'gen_time_table')
    def _onchange_slot_id(self):
        if self.slot_id:
            self.session_start_time = self.slot_id.starting_time
            self.session_end_time = self.slot_id.ending_time
