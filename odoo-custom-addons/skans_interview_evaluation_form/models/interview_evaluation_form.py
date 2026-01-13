from odoo import models, api, fields
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta, date
import logging
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)


class EvaluationForm(models.Model):
    _name = 'evaluation.form'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    candidate_name = fields.Many2one('hr.candidate', string="Candidate", store=True, tracking=True)
    interviewer_name = fields.Many2one('res.users', string="Interviewer", store=True, tracking=True)
    interview_date = fields.Date(string="Interview Date", store=True, tracking=True)
    position = fields.Many2one('hr.job', string="Position", store=True, tracking=True)
    template_id = fields.Many2one('interview.form.template', string="Template", store=True, tracking=True,
                                  required=True)
    line_ids = fields.One2many('evaluation.form.line', 'evaluation_id', string="Rating Criteria")
    comments = fields.Html(string="Comments", store=True, tracking=True)
    total_marks = fields.Integer(string="Obtained Marks", compute="_compute_marks", store=True)
    total_possible_marks = fields.Integer(string="Total Marks", compute="_compute_marks", store=True)
    percentage = fields.Float(string="Percentage", compute="_compute_marks", store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company.id)
    company_logo = fields.Binary(string="Company Logo", compute="_compute_company_logo", store=False)
    # line_ids = fields.One2many('interview.form.template.line', 'template_id', string="Rating Criteria")
    state = fields.Selection([
        ('not_approved', 'Not Approved'),
        ('approved_with_reser', 'Approved With Reservation'),
        ('approved', 'Approved'),
    ], default=False, track_visibility='always')
    status_appr = fields.Boolean(string="Approved", store=True, tracking=True, default=False)
    status_not_appr = fields.Boolean(string="Not Approved", store=True, tracking=True, default=False)
    status_appr_res = fields.Boolean(string="Approved With Reservation", store=True, tracking=True, default=False)

    @api.depends('company_id')
    def _compute_company_logo(self):
        for record in self:
            record.company_logo = record.company_id.logo

    def action_not_appr(self):
        self.write({'state': 'not_approved'})
        self.status_not_appr = True

    def action_appr_reser(self):
        self.write({'state': 'approved_with_reser'})

        self.status_appr_res = True

    def action_approved(self):
        self.write({'state': 'approved'})
        self.status_appr = True

    @api.depends('line_ids.rating_1', 'line_ids.rating_2', 'line_ids.rating_3', 'line_ids.rating_4',
                 'line_ids.rating_5')
    def _compute_marks(self):
        for rec in self:
            total = 0
            for line in rec.line_ids:
                if line.rating_1:
                    total += 1
                elif line.rating_2:
                    total += 2
                elif line.rating_3:
                    total += 3
                elif line.rating_4:
                    total += 4
                elif line.rating_5:
                    total += 5
            total_lines = len(rec.line_ids)
            rec.total_marks = total
            rec.total_possible_marks = total_lines * 5
            rec.percentage = round((total / rec.total_possible_marks * 100), 2) if rec.total_possible_marks else 0.0

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            _logger.info(self.template_id.line_ids)
            _logger.info('self.template_iddddddddddddddddddddddddd')
            _logger.info('self.template_iddddddddddddddddddddddddd')
            _logger.info('self.template_iddddddddddddddddddddddddd')
            _logger.info('self.template_iddddddddddddddddddddddddd')
            _logger.info('self.template_iddddddddddddddddddddddddd')
            self.line_ids = [(5, 0, 0)]  # clear existing lines
            self.line_ids = [
                (0, 0, {
                    'criteria': line.criteria,
                    'rating_1': line.rating_1,
                    'rating_2': line.rating_2,
                    'rating_3': line.rating_3,
                    'rating_4': line.rating_4,
                    'rating_5': line.rating_5,
                }) for line in self.template_id.line_ids
            ]


class EvaluationFormLine(models.Model):
    _name = 'evaluation.form.line'
    _description = 'Evaluation Form Line'

    evaluation_id = fields.Many2one('evaluation.form', string="Evaluation Form", ondelete="cascade")
    criteria = fields.Char(string="Criteria")
    # rating = fields.Selection([('5', '5'), ('4', '4'), ('3', '3'), ('2', '2'), ('1', '1')], string="Rating")
    rating_1 = fields.Boolean(string="1")
    rating_2 = fields.Boolean(string="2")
    rating_3 = fields.Boolean(string="3")
    rating_4 = fields.Boolean(string="4")
    rating_5 = fields.Boolean(string="5")

    @api.onchange('rating_1')
    def _onchange_rating1_checkboxes(self):
        for rec in self:
            if rec.rating_1:
                rec.rating_2 = rec.rating_3 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_2')
    def _onchange_rating2_checkboxes(self):
        for rec in self:
            if rec.rating_2:
                rec.rating_1 = rec.rating_3 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_3')
    def _onchange_rating3_checkboxes(self):
        for rec in self:
            if rec.rating_3:
                rec.rating_2 = rec.rating_1 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_4')
    def _onchange_rating4_checkboxes(self):
        for rec in self:
            if rec.rating_4:
                rec.rating_2 = rec.rating_3 = rec.rating_1 = rec.rating_5 = False

    @api.onchange('rating_5')
    def _onchange_rating5_checkboxes(self):
        for rec in self:
            if rec.rating_5:
                rec.rating_2 = rec.rating_3 = rec.rating_4 = rec.rating_1 = False
