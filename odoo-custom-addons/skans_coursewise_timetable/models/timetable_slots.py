from odoo import models, fields, api
from odoo.addons.lunch.models.lunch_supplier import float_to_time


class TimetableSlots(models.Model):
    _name = 'op.timetable.slots'
    _rec_name = 'display_time_field'

    course_id_slot = fields.Many2one('op.course', string='Course')
    starting_time = fields.Float(string='Start Time')
    ending_time = fields.Float(string='End Time')
    duration_time = fields.Float(string='Interval (In minutes)')
    display_time_field = fields.Char(compute='display_slot_time',string='Display Slot Time')

    def float_to_time_string(self, float_hour):
        hours = int(float_hour)
        minutes = int(round((float_hour - hours) * 60))
        return f"{hours:02d}:{minutes:02d}"

    @api.depends('starting_time', 'ending_time')
    def display_slot_time(self):
        for record in self:
            if record.starting_time and record.ending_time:
                start_str = record.float_to_time_string(record.starting_time)
                end_str = record.float_to_time_string(record.ending_time)
                record.display_time_field = f"{start_str} - {end_str}"
            else:
                record.display_time_field = ""


