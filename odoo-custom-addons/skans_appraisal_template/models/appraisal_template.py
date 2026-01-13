# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SkansAppraisalTemplate(models.Model):
    _name = 'appraisal.template'

    name = fields.Char(string="Template Name", required=True)
    template_type = fields.Boolean(string="Appraisal Form", store=True, tracking=True, default=False)
    line_ids = fields.One2many('appraisal.form.template.line', 'template_id', string="Rating Criteria")


class InterviewFormTemplateLine(models.Model):
    _name = 'appraisal.form.template.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    template_id = fields.Many2one('appraisal.template', string="Template")
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
            # If any rating checkbox is selected, set all others to False
            if rec.rating_1:
                rec.rating_2 = rec.rating_3 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_2')
    def _onchange_rating2_checkboxes(self):
        for rec in self:
            # If any rating checkbox is selected, set all others to False
            if rec.rating_2:
                rec.rating_1 = rec.rating_3 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_3')
    def _onchange_rating3_checkboxes(self):
        for rec in self:
            # If any rating checkbox is selected, set all others to False
            if rec.rating_3:
                rec.rating_2 = rec.rating_1 = rec.rating_4 = rec.rating_5 = False

    @api.onchange('rating_4')
    def _onchange_rating4_checkboxes(self):
        for rec in self:
            # If any rating checkbox is selected, set all others to False
            if rec.rating_4:
                rec.rating_2 = rec.rating_3 = rec.rating_1 = rec.rating_5 = False

    @api.onchange('rating_5')
    def _onchange_rating5_checkboxes(self):
        for rec in self:
            # If any rating checkbox is selected, set all others to False
            if rec.rating_5:
                rec.rating_2 = rec.rating_3 = rec.rating_4 = rec.rating_1 = False
