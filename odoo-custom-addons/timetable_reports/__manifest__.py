{
    'name' : 'Timetable reports',
    'version': '18.0',
    'author': 'Asad',
    'category': 'Productivity',
    'Summary': 'This addon is for timetable report',
    'depends' : ['report_xlsx', 'gxs_timetable', 'base'],
    'description': """'This addon is for timetable report'""",

    'data':[
        'views/timetable_views.xml',
        # 'views/report_actions.xml',
        'views/timetable_pdf.xml',
    ],


   'installable':True,
    'auto install':False,
}