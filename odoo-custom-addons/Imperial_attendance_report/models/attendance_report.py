import logging
from datetime import datetime, timedelta

import pytz

from odoo import models, fields

karachi_tz = pytz.timezone('Asia/Karachi')

_logger = logging.getLogger(__name__)


class DailyAttendanceReportEmployee(models.TransientModel):
    _name = 'daily.attendance.report.employee'
    _description = "Attendance Report Wizard"

    from_date = fields.Date('To Date', required=True)
    to_date = fields.Date('From Date', required=True)
    department = fields.Many2one('hr.department', string="Department")
    shift = fields.Many2one('resource.calendar', string="Shift")

    def print_report(self):
        record_list = []
        attendance_domain = [
            ('check_in', '>=', f"{self.from_date} 00:00:00"),
            ('check_in', '<=', f"{self.from_date} 23:59:59"),
        ]

        if self.department:
            attendance_domain.append(('employee_id.department_id', '=', self.department.id))

        if self.shift:
            attendance_domain.append(('employee_id.resource_calendar_id', '=', self.shift.id))

        attendance = self.env['hr.attendance'].search(attendance_domain)

        for rec in attendance:
            # attendannce = sum(self.env['sg.atten.policy.dep'].search(
            #     [('department_ids', 'in', rec.employee_id.department_id.ids)]).mapped('time'))

            hours = int(rec.late_emp)
            minutes = int((rec.late_emp - hours) * 60)
            if hours <= 0:
                hours = 0
            if minutes <= 0:
                minutes = 0
            # late_by_time = "{:02d}:{:02d}".format(hours, minutes)
            previous_date = (datetime.strptime(self.from_date.strftime('%Y-%m-%d'), '%Y-%m-%d') - timedelta(
                days=1)).strftime('%Y-%m-%d')
            previous_day_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('check_in', '>=', f"{self.to_date} 00:00:00"),
                ('check_in', '<=', f"{self.to_date} 23:59:59")
            ])

            pre_hours = 0
            pre_minutes = 0
            pre_seconds = 0
            check_in_datetime = False
            check_out_datetime = False

            if previous_day_attendance:
                pre_hours = int(previous_day_attendance.late_emp)
                pre_minutes = int((previous_day_attendance.late_emp - pre_hours) * 60)
                if pre_hours <= 0:
                    pre_hours = 0
                if pre_minutes <= 0:
                    pre_minutes = 0

                if previous_day_attendance.check_in:
                    check_in_datetime = previous_day_attendance.check_in.replace(tzinfo=pytz.utc).astimezone(karachi_tz)

                if previous_day_attendance.check_out:
                    check_out_datetime = previous_day_attendance.check_out.replace(tzinfo=pytz.utc).astimezone(
                        karachi_tz)

            record_list.append({
                'name': rec.employee_id.name,
                'batch': rec.employee_id.barcode,
                'designation': rec.employee_id.department_id.name,
                'datee': rec.check_in.date().strftime('%Y-%m-%d'),
                'in_time': rec.check_in.replace(tzinfo=pytz.utc).astimezone(karachi_tz).strftime('%H:%M'),
                'late_by_time': "{:02d}:{:02d}".format(hours, minutes),
                'pre_datee': check_in_datetime.strftime('%Y-%m-%d') if check_in_datetime else False,
                'pre_in_time': check_in_datetime.strftime('%H:%M') if check_in_datetime else False,
                'pre_late_by_time': "{:02d}:{:02d}".format(pre_hours, pre_minutes),
                'pre_out_time': check_out_datetime.strftime('%H:%M') if check_out_datetime else False,
            })
            _logger.info(record_list)

        res = {
            'record_list': record_list,
            'company_name': self.env.user.company_id.name,
            'company_logo': self.env.user.company_id.logo,
            'pre_datee': self.to_date,
            'datee': self.from_date,

        }
        data = {
            'form_data': self.read()[0],
            'rec': res,

        }
        return self.env.ref('Imperial_attendance_report.daily_attendance_report').report_action(self, data=data)
