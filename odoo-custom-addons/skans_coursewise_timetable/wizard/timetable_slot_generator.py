from odoo import models, fields, api


class TimetableSlotGenerator(models.TransientModel):
    _name = 'timetable.slot.generator'

    slot_course_id = fields.Many2one('op.course', string='Course')
    starting_slot_time = fields.Float(string='Start Time', required=True)
    ending_slot_time = fields.Float(string='End Time', required=True)
    interval_slot_time = fields.Float(string="Interval (in minutes)", required=True)


    def action_timetable_slot_generator(self):
        self.ensure_one()
        course_id = self.slot_course_id
        current_time = self.starting_slot_time
        end_time = self.ending_slot_time
        interval_hours = self.interval_slot_time

        while current_time < end_time:
            next_time = current_time + interval_hours
            if next_time > end_time:
                next_time = end_time

            self.env['op.timetable.slots'].create({
                'course_id_slot':course_id.id,
                'starting_time': current_time,
                'ending_time': next_time,
                'duration_time': next_time - current_time,
            })

            current_time = next_time


