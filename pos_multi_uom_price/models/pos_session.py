# -*- coding: utf-8 -*-
# © 2026 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from odoo import models, api


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def _load_pos_data_models(self, config):
        data = super()._load_pos_data_models(config)
        data += ['product.multi.uom.price']
        return data
