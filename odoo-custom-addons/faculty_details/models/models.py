from odoo import models, fields, api


class OpFaculty(models.Model):
    _inherit = 'op.faculty'

    @api.onchange('emp_id')
    def onchange_emp_id(self):
        for rec in self:
            if rec.emp_id:
                rec.email = rec.emp_id.work_email
                rec.phone = rec.emp_id.work_phone
                rec.mobile = rec.emp_id.mobile_phone
                rec.birth_date = rec.emp_id.birthday
                rec.gender = rec.emp_id.gender
                rec.blood_group = rec.emp_id.emp_blood_groups
                rec.nationality = rec.emp_id.country_id
                rec.street = rec.emp_id.emp_permanent_street1
                rec.street2 = rec.emp_id.emp_permanent_street2
                rec.city = rec.emp_id.emp_permanent_city
                rec.state_id = rec.emp_id.emp_permanent_state_id
                rec.zip = rec.emp_id.emp_permanent_zip
                rec.country_id = rec.emp_id.emp_permanent_country_id
