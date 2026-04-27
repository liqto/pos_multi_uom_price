# -*- coding: utf-8 -*-
# © 2026 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

import logging

from odoo import models, fields, api, _
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)
    
class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    product_uom_id = fields.Many2one('uom.uom', string='Product Unit', related='')  

    @api.model
    def _load_pos_data_fields(self, config_id):
        params = super()._load_pos_data_fields(config_id)
        params += ['product_uom_id']
        return params

    def _compute_total_cost(self, stock_moves):
        """
        Compute the total cost of the order lines.
        :param stock_moves: recordset of `stock.move`, used for fifo/avco lines
        """
        for line in self.filtered(lambda l: not l.is_total_cost_computed):
            product = line.product_id
            cost_currency = product.sudo().cost_currency_id
            if line._is_product_storable_fifo_avco() and stock_moves:
                moves = line._get_stock_moves_to_consider(stock_moves, product)
                product_cost = moves._get_price_unit()
                if (cost_currency.is_zero(product_cost) and line.order_id.shipping_date and line.refunded_orderline_id):
                    product_cost = line.refunded_orderline_id.total_cost / line.refunded_orderline_id.qty
                product_cost = line.product_uom_id.factor * product_cost / product.uom_id.factor
            else:
                product_cost = line.product_uom_id.factor * product.standard_price / product.uom_id.factor
            line.total_cost = line.qty * cost_currency._convert(
                from_amount=product_cost,
                to_currency=line.currency_id,
                company=line.company_id or self.env.company,
                date=line.order_id.date_order or fields.Date.today(),
                round=False,
            )
            line.is_total_cost_computed = True
            
