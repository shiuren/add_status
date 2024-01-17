# -*- coding: utf-8 -*-
{
    'name': "Dossier",

    'summary': "",

    'description': "",

    'author': "MTechniix",
    'website': "https://www.mtechniix.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/folder_model.xml',
        'views/cession_model.xml',
        'views/regul_model.xml',
        'views/dhl_model.xml',
        'views/tc_model.xml',
        'reports/folder_report_complete_template.xml',
        'reports/folder_report_inprogress_template.xml',
        'reports/folder_report_complete.xml',
        'reports/folder_report_inprogress.xml',
        'reports/report_folder.xml',
        'reports/report_folder_template.xml',
        'views/menus.xml',
    ],
    'assets':{
        'web.assets_backend':[
            "/mtx_folder/static/src/styles/backend.scss",
        ]
    }
}
