from odoo import models, api
from odoo import models, fields, api

from odoo.exceptions import ValidationError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def copy(self, default=None):
        new_employee = super().copy(default)

        for experience in self.experience_skans_ids:
            new_experience = experience.copy()
            new_experience.employee_id = new_employee.id
        for job_reference in self.job_reference_ids:
            new_job_reference = job_reference.copy()
            new_job_reference.employee_id = new_employee.id
        for verification_status in self.verification_status_ids:
            new_verification_status = verification_status.copy()
            new_verification_status.employee_id = new_employee.id
        for project_summary in self.project_employee_ids:
            new_project_summary = project_summary.copy()
            new_project_summary.employee_id = new_employee.id
        for kin in self.kin_ids:
            new_kin = kin.copy()
            new_kin.employee_id = new_employee.id
        for collab in self.collab_id:
            new_collab = collab.copy()
            new_collab.employee_id = new_employee.id
        for education in self.education_id:
            new_education = education.copy()
            new_education.employee_id = new_employee.id
        for verify_body in self.verify_body_id:
            new_verify_body = verify_body.copy()
            new_verify_body.employee_id = new_employee.id
        for additional_duties in self.additional_duties_emp_ids:
            new_additional_duties = additional_duties.copy()
            new_additional_duties.employee_id = new_employee.id
        for training_courses_taught in self.training_courses_taught_ids:
            new_training_courses_taught = training_courses_taught.copy()
            new_training_courses_taught.employee_id = new_employee.id
        for employee_record in self.employee_records_ids:
            new_employee_record = employee_record.copy()
            new_employee_record.employee_id = new_employee.id
        for child in self.child_details_ids:
            new_child = child.copy()
            new_child.employee_id = new_employee.id
        for increment in self.increment_ids:
            new_increment = increment.copy()
            new_increment.employee_id = new_employee.id
        for professional in self.professional_details_ids:
            new_professional = professional.copy()
            new_professional.employee_id = new_employee.id
        for verification_detail in self.verification_details_ids:
            new_verification_detail = verification_detail.copy()
            new_verification_detail.employee_id = new_employee.id
        for reg in self.reg_id:
            new_reg = reg.copy()
            new_reg.employee_id = new_employee.id
        for project in self.project_employee_ids:
            new_project = project.copy()
            new_project.employee_id = new_employee.id
        for training_courses in self.training_courses_emp_ids:
            new_training_courses = training_courses.copy()
            new_training_courses.employee_id = new_employee.id
        for honor in self.honor_ids:
            new_honor = honor.copy()
            new_honor.employee_id = new_employee.id
        for scholarship in self.scholarship_ids:
            new_scholarship = scholarship.copy()
            new_scholarship.employee_id = new_employee.id
        for supervision in self.supervision_ids:
            new_supervision = supervision.copy()
            new_supervision.employee_id = new_employee.id

        return new_employee
