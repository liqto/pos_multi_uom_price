# -*- coding: utf-8 -*-
# © 2026 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

import logging

from odoo import models

_logger = logging.getLogger(__name__)

class SaleReport(models.Model):
    _inherit = "sale.report"

    def _query(self):
        query = super()._query()
        if "LEFT JOIN uom_uom uu ON uu.id = l.product_uom_id" not in query:
            query = query.replace(
                "LEFT JOIN uom_uom u ON u.id=t.uom_id",
                "LEFT JOIN uom_uom u ON u.id=t.uom_id\n"
                "LEFT JOIN uom_uom uu ON uu.id = l.product_uom_id"
            )
            query = query.replace(
                "SUM(l.qty) AS product_uom_qty,",
                "SUM(uu.factor * l.qty / u.factor) AS product_uom_qty,"
            ).replace(
                "SUM(l.qty_delivered) AS qty_delivered,",
                "SUM(uu.factor * l.qty_delivered / u.factor) AS qty_delivered,"
            ).replace(
                "SUM(l.qty - l.qty_delivered) AS qty_to_deliver,",
                "SUM(uu.factor * (l.qty - l.qty_delivered) / u.factor) AS qty_to_deliver,"
            )
        return query