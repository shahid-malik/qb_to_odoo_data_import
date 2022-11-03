# -*- coding: utf-8 -*-
{
    'name': 'Sales Product Image URL',
    'version': '0.1',
    'development_status': 'Production/Stable',
    'category': 'Sales',
    'summary': 'Add ability to specify image by URL',
    'license': 'Other proprietary',
    'author': '',
    'website': '',
    'images': [
        '',
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'depends': [
        'sale_management',
        'product',
        'website_sale',
    ],
    'data': [
        'views/extra_image_url.xml',
    ],
}
