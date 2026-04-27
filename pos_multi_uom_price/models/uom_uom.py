# -*- coding: utf-8 -*-
# © 2026 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from odoo import models, fields, api, _

class UomUom(models.Model):
    _inherit = 'uom.uom'

    root_parent_path = fields.Char(
        compute='_compute_root_parent_path',
        store=True,
        index=True,
    )

    @api.depends('parent_path')
    def _compute_root_parent_path(self):
        for uom in self:
            if uom.parent_path:
                uom.root_parent_path = uom.parent_path.split('/')[0]
            else:
                uom.root_parent_path = False
