{
    "name": "Faculty Result Summary",
    "version": "1.0",
    "category": "Reporting",
    "summary": "Faculty wise result summary with percentages",
    "depends": ["base", "web", "gxs_student_performance", "gxs_core"],
    "data": [
        "security/ir.model.access.csv",
        "views/faculty_result_summary_wizard_view.xml",
        "reports/faculty_result_summary_template.xml"
    ],
    "installable": True,
    "application": True
}