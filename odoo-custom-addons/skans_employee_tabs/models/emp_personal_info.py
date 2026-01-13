from odoo import models, fields, api
from datetime import date

from odoo.exceptions import ValidationError


class PersonalDetailsManagement(models.Model):
    _inherit = 'hr.employee'

    emp_religion = fields.Selection(
        [('muslim', 'Muslim'), ('hindu', 'Hindu'), ('christian', 'Christian'), ('jewish', 'Jewish'),
         ('atheist', 'Atheist')], string='Religion')
    emp_sect = fields.Selection([('sunni', 'Sunni'),('shia', 'Shia'),('wahhabi', 'Wahhabi'),('salafi', 'Salafi'),('barelvi', 'Barelvi'),('deobandi', 'Deobandi'),], string="Sect")
    secondary_country = fields.Many2one('res.country', string='Secondary Country')
    emp_domicile = fields.Char(string='Domicile')
    emp_blood_groups = fields.Selection([
        ('a+', 'A+'),
        ('a-', 'A-'),
        ('b+', 'B+'),
        ('b-', 'B-'),
        ('ab+', 'AB+'),
        ('ab-', 'AB-'),
        ('o+', 'O+'),
        ('o-', 'O-'),
    ], string="Blood Group")

    emp_age_field = fields.Char(string='Age', compute='calculate_emp_age')
    emp_marital_field = fields.Selection([('single', 'Single'), ('married', 'Married'),
                                          ('legal_cohabitant', 'Legal Cohabitant'),
                                          ('widower', 'Widower'), ('divorced', 'Divorced')], string='Marital Status')

    # mailing address

    emp_mailing_street1 = fields.Char(string='Street1')
    emp_mailing_street2 = fields.Char(string='Street2')
    emp_mailing_city = fields.Char(string='City')
    emp_mailing_state_id = fields.Char(string='State')
    emp_mailing_zip = fields.Char(string='Zip')
    emp_mailing_country_id = fields.Many2one('res.country', string='Country')

    # permanent address

    emp_permanent_street1 = fields.Char(string='Street1')
    emp_permanent_street2 = fields.Char(string='Street2')
    emp_permanent_city = fields.Char(string='City')
    emp_permanent_state_id = fields.Char(string='State')
    emp_permanent_zip = fields.Char(string='Zip')
    emp_permanent_country_id = fields.Many2one('res.country', string='Country')

    emp_primary_phone_number = fields.Char(string='Primary PH')
    emp_secondary_phone_number = fields.Char(string='Secondary PH')
    emp_landline_home_number = fields.Char(string='Landline Home')
    emp_landline_office_number = fields.Char(string='Landline Office')
    emp_skype_id = fields.Char(string='Skype')
    emp_email_personal = fields.Char(string='Personal Email')
    emp_email_official = fields.Char(string='Official Email')
    emp_social_media_profile = fields.Char(string='Social Media Link')

    emp_employed_from = fields.Char(string='Employed From')
    emp_credit_load = fields.Char(string='Credit Load')
    emp_flag_status = fields.Selection([('faculty', 'Faculty'), ('staff', 'Staff'), ('employee', 'Employee')],
                                       string='Flag Status')

    @api.depends('birthday')
    def calculate_emp_age(self):
        for rec in self:
            if rec.birthday:
                today = date.today()
                if rec.birthday < today:
                    emp_age_year = today.year - rec.birthday.year
                    emp_age_month = today.month - rec.birthday.month
                    emp_age_day = today.day - rec.birthday.day

                    if emp_age_day < 0:
                        emp_age_month -= 1
                        prev_month = today.month - 1 or 12
                        prev_year = today.year if today.month != 1 else today.year - 1
                        from calendar import monthrange
                        days_in_prev_month = monthrange(prev_year, prev_month)[1]
                        emp_age_day += days_in_prev_month

                    if emp_age_month < 0:
                        emp_age_year -= 1
                        emp_age_month += 12

                    rec.emp_age_field = f"{emp_age_year if emp_age_year else 0} Y, {emp_age_month if emp_age_month else 0} M and {emp_age_day if emp_age_day else 0} D."

                else:
                    raise ValidationError("Invalid Birth Date Given")

            else:
                rec.emp_age_field = 0
