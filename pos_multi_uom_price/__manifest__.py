# -*- coding: utf-8 -*-
# © 2026 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

{
    'name': "POS multi uom price",
    'summary': 'POS Price per unit of measure',
    'category': 'Point of Sale',
    'version': '19.0.1.0.1',
    'license': "AGPL-3",
    'description': """
        With this module you can sell your products with different units of measure in POS.
    """,

    'author': "ehuerta _at_ ixer.mx",
    'depends': ['point_of_sale', 'pos_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
    ],
    'images': [
        'static/description/POS_multi_uom_price.png',
    ],
    'installable': True,
    'auto_install': False,
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_multi_uom_price/static/src/**/*',
        ],
    },
}
