from odoo import models, fields, api
from datetime import timedelta


class Attendance(models.Model):
    _inherit = 'hr.attendance'

    late_counts = fields.Integer(string='Late Counts', readonly=True)

    def create(self, vals):
        attendance = super(Attendance, self).create(vals)

        if attendance.check_out:
            print('Start')
            employee = attendance.employee_id
            check_out = fields.Datetime.from_string(attendance.check_out)

            # allocated_leave = self.env['hr.leave.allocation'].search([
            #     ('employee_id', '=', employee.id),
            #     ('holiday_status_id.name', '=', 'Casual Leave'),
            #     ('state', '=', 'validate'),
            #     ('number_of_days_display', '>', 0),
            #     ('date_from', '<=', check_out.date()),
            #     ('date_to', '>=', check_out.date()),
            # ], limit=1, order="id")

            # print(allocated_leave.holiday_status_id.name)

            resource_calendar = employee.resource_calendar_id
            if resource_calendar:
                weekday_str = str(check_out.weekday())
                # for line in resource_calendar.attendance_ids:
                #     print(
                #         f'Day: {line.dayofweek}, Period: {line.day_period}, From: {line.hour_from}, To: {line.hour_to}')

                day_schedule = resource_calendar.attendance_ids.filtered(
                    lambda r: r.dayofweek == weekday_str
                )
                print(day_schedule)
                if day_schedule:
                    print('schedule found')
                    max_hour = max(day_schedule.mapped('hour_to'))
                    scheduled_check_out = check_out.replace(hour=int(max_hour), minute=int((max_hour % 1) * 60), second=0)
                    print(scheduled_check_out)

                    if check_out < (scheduled_check_out - timedelta(minutes=15)):
                        print('penalty')
                        first_day_of_month = check_out.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        previous_early_departures = self.search_count([
                            ('employee_id', '=', employee.id),
                            ('late_counts', '>', 0),
                            ('check_out', '>=', first_day_of_month),
                        ])

                        attendance.late_counts = previous_early_departures + 1
                        print(attendance.late_counts)

                        if attendance.late_counts > 2:
                            print('time to make a leave')
                            # leave_types = ['Casual Leave', 'Sick Leave', 'Annual Leave']

                            leave_types = [
                                self.env['hr.leave.type'].search([('name', '=', 'Casual Leave')], limit=1),
                                self.env['hr.leave.type'].search([('name', '=', 'Annual Leave')], limit=1),
                                self.env['hr.leave.type'].search([('name', '=', 'Sick Leave')], limit=1),
                            ]
                            for leave in leave_types:

                                allocated_leave = self.env['hr.leave.allocation'].search([
                                    ('employee_id', '=', employee.id),
                                    ('holiday_status_id', '=', leave.id),
                                    ('state', '=', 'validate'),
                                    ('number_of_days_display', '>', 0),
                                    ('date_from', '<=', check_out.date()),
                                    ('date_to', '>=', check_out.date()),
                                ])

                                print(allocated_leave.holiday_status_id.name)

                                used_leaves = self.env['hr.leave'].search_count([
                                    ('employee_id', '=', employee.id),
                                    ('holiday_status_id', '=', leave.id),
                                    ('state', 'in', ['validate', 'confirm', 'draft']),  # include all relevant ones
                                    ('request_date_from', '>=', allocated_leave.date_from),
                                    ('request_date_to', '<=', allocated_leave.date_to),
                                ])

                                # print(
                                #     f"Used leaves for {leave.name}: {used_leaves} / {allocated_leave.number_of_days_display}")

                                if used_leaves >= allocated_leave.number_of_days_display:
                                    print(f"{leave.name} fully used, moving to next...")
                                    continue

                                if allocated_leave:
                                        print('found allocation', allocated_leave)
                                        self.env['hr.leave'].create({
                                            'name': 'Auto Leave due to Early Departures',
                                            'holiday_status_id': allocated_leave.holiday_status_id.id,
                                            'employee_id': employee.id,
                                            'request_date_from': check_out.date(),
                                            'request_date_to': check_out.date(),
                                            'date_from': check_out.replace(hour=9, minute=0),
                                            'date_to': check_out.replace(hour=18, minute=0),
                                        })
                                        print('leave created')
                                        break
        return attendance

