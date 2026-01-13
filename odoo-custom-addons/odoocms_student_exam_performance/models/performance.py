from odoo import models, fields, api


    
class OdoocmsPerformanceTemplate(models.Model):
    _name = 'odoocms.performance.template'
    _description = 'Performance Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    # section_id = fields.Many2one('class.section', string="Section")
    performance_template_line_ids = fields.One2many('odoocms.performance.template.line', 'performance_template_id', string='Performance Grade')
   
    
    
    
    
class OdoocmsPerformanceTemplateLine(models.Model):
    _name = 'odoocms.performance.template.line'
    _description = 'Performance Template lines'
    
    name = fields.Char(string="Name")
    performance_type = fields.Selection([
        ('E', 'E'),
        ('G', 'G'),
        ('S', 'S'),
        ('NI', 'NI'),
    ], string="Type", required=True)

    section_id = fields.Many2one('class.section', string="Section")
    performance_template_id = fields.Many2one("odoocms.performance.template", string="Performance")
    std_performance_id = fields.Many2one("gxs.std.performance", string="STD Performance")
    # std_result_id = fields.Many2one("gxs.std.result", string="STD Result")
