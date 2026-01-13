from odoo import models, fields, api
import pytz
from datetime import datetime, time


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    early_departure = fields.Float(
        string="Early Departure (hours)",
        compute='_compute_early_departure',
        store=True,
        help="Hours left early based on scheduled end"
    )

    @api.constrains('early_departure')
    def onchange_early_departure(self):
        for rec in self:
            if rec.early_departure > 1.50:
                print('I am here')
                if rec.employee_id.employee_type_2 == 'college':
                    print('now here')
                    leave_type = self.env['hr.leave.type'].search([('name', '=', 'Short Leave')], limit=1)

                    if not leave_type:
                        continue

                    existing_leave = self.env['hr.leave'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('holiday_status_id', '=', leave_type.id),
                        ('date_from', '=', rec.check_in),
                        ('date_to', '=', rec.check_out),
                    ], limit=1)

                    if existing_leave:
                        continue

                    leave_date = rec.check_in.date()
                    tz = pytz.timezone(rec.employee_id.tz or 'UTC')
                    local_from = datetime.combine(leave_date, time(13, 0))
                    local_to = datetime.combine(leave_date, time(17, 0))

                    utc_from = tz.localize(local_from).astimezone(pytz.UTC)
                    utc_to = tz.localize(local_to).astimezone(pytz.UTC)

                    leave_date_from = utc_from.replace(tzinfo=None)
                    leave_date_to = utc_to.replace(tzinfo=None)


                    leave = self.env['hr.leave'].with_context(skip_compute_dates=True).create({
                        'name': 'Auto Short Leave (Early Departure)',
                        'employee_id': rec.employee_id.id,
                        'holiday_status_id': leave_type.id,
                        'request_date_from': leave_date,
                        'request_date_to': leave_date,
                        'request_unit_half': True,
                        'request_date_from_period': 'pm',
                        'date_from': leave_date_from,
                        'date_to': leave_date_to,
                    })


    @api.depends('check_out', 'employee_id')
    def _compute_early_departure(self):
        for attendance in self:
            early = 0.0

            if attendance.check_out and attendance.employee_id and attendance.employee_id.resource_calendar_id:

                tz = pytz.timezone(attendance.employee_id.tz or 'UTC')
                check_out_local = attendance.check_out.astimezone(tz)

                day_of_week = str(check_out_local.weekday())

                calendar = attendance.employee_id.resource_calendar_id
                day_intervals = calendar.attendance_ids.filtered(
                    lambda x: str(x.dayofweek) == day_of_week
                )

                if day_intervals:
                    last_interval = max(day_intervals, key=lambda i: i.hour_to)

                    scheduled_hour = int(last_interval.hour_to)
                    scheduled_minute = int((last_interval.hour_to - scheduled_hour) * 60)

                    scheduled_end = tz.localize(datetime.combine(
                        check_out_local.date(),
                        time(scheduled_hour, scheduled_minute)
                    ))

                    if check_out_local < scheduled_end:
                        diff_hours = (scheduled_end - check_out_local).total_seconds() / 3600.0
                        early = round(diff_hours, 2)

            attendance.early_departure = early



class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.depends('request_date_from', 'request_date_to', 'request_unit_half', 'request_unit_hours')
    def _compute_date_from_to(self):
        if self.env.context.get('skip_compute_dates'):
            return
        super(HrLeave, self)._compute_date_from_to()
