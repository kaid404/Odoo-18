from odoo import models, fields, api


class ClassSection(models.Model):
	_inherit = "class.section"
	
	performance_ids = fields.Many2one('odoocms.performance.template', string='Performance')
	section_performance_line_ids = fields.One2many('odoocms.performance.template.line', 'section_id',
	                                               string="Performance Lines")
	
	@api.onchange('performance_ids')
	def _onchange_performance_ids(self):
		if self.performance_ids:
			self.section_performance_line_ids = [(5, 0, 0)]
			new_lines = []
			for line in self.performance_ids.performance_template_line_ids:
				new_lines.append((0, 0, {
					'name': line.name,
					'performance_type': line.performance_type,
				}))
			self.section_performance_line_ids = new_lines


class StudentPerformance(models.Model):
	_inherit = "gxs.std.performance"
	
	
	section_performance_line_ids = fields.One2many('odoocms.performance.template.line', 'std_performance_id',
	                                               string="Performance Lines")
	
	@api.onchange('section_id')
	def _onchange_section_id(self):
		if self.section_id:
			# Clear previous lines
			self.section_performance_line_ids = [(5, 0, 0)]
			
			# Copy lines from section
			new_lines = []
			for line in self.section_id.section_performance_line_ids:
				new_lines.append((0, 0, {
					'name': line.name,
					'performance_type': line.performance_type,
				}))
			self.section_performance_line_ids = new_lines
			
#
# class GXSStudentResult(models.Model):
# 	_inherit = "gxs.std.result"
#
#
# 	section_performance_line_ids = fields.One2many('odoocms.performance.template.line', 'std_result_id',
# 	                                               string="Performance Lines")
#
# 	@api.onchange('section_id')
# 	def _onchange_section_id(self):
# 		if self.section_id:
# 			# Clear previous lines
# 			self.section_performance_line_ids = [(5, 0, 0)]
#
# 			# Copy lines from section
# 			new_lines = []
# 			for line in self.section_id.section_performance_line_ids:
# 				new_lines.append((0, 0, {
# 					'name': line.name,
# 					'performance_type': line.performance_type,
# 				}))
# 			self.section_performance_line_ids = new_lines