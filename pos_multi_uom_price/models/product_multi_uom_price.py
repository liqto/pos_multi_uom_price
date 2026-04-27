# -*- coding: utf-8 -*-
# © 2026 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class prod_tmpl_multi_uom(models.Model):
    _name = 'product.tmpl.multi.uom.price'
    _description = 'Product template multiple uom price'

    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
        ondelete="cascade",
        readonly=True
    )
    product_root_parent_path = fields.Char(related='product_tmpl_id.uom_id.root_parent_path', store=False,)
    uom_id = fields.Many2one('uom.uom',
        string = "Unit of Measure",
        domain="[('root_parent_path', '=', product_root_parent_path)]",
        required = True
    )
    price = fields.Float('Price',
        required=True,
        digits='Product Price'
    )


    def _sync_price_to_variants(self):
        ProductMultiUom = self.env['product.multi.uom.price']
        variant_uom_keys = []
        existing_prices_map = {}
        for rec in self:
            for variant in rec.product_tmpl_id.product_variant_ids:
                variant_uom_keys.append((variant.id, rec.uom_id.id))
        if variant_uom_keys:
            existing_prices = ProductMultiUom.search([
                ('product_id', 'in', [v for v, _ in variant_uom_keys]),
                ('uom_id', 'in', [u for _, u in variant_uom_keys])
            ])
            for price in existing_prices:
                existing_prices_map[(price.product_id.id, price.uom_id.id)] = price
        to_create = []
        for rec in self:
            for variant in rec.product_tmpl_id.product_variant_ids:
                key = (variant.id, rec.uom_id.id)
                existing = existing_prices_map.get(key)
                if existing:
                    if existing.price != rec.price:
                        existing.price = rec.price
                else:
                    to_create.append({
                        'product_id': variant.id,
                        'uom_id': rec.uom_id.id,
                        'price': rec.price,
                    })
        if to_create:
            ProductMultiUom.create(to_create)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sync_price_to_variants()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._sync_price_to_variants()
        return res

    _product_tmpl_uom_unique = models.Constraint(
         'UNIQUE(product_tmpl_id, uom_id)',
         'Each Unit of Measure must be unique per product template.')

    @api.constrains('uom_id', 'product_tmpl_id')
    def _check_uom_compatibility(self):
        for rec in self:
            if not rec.uom_id or not rec.product_tmpl_id.uom_id:
                continue
            if not rec.uom_id._has_common_reference(rec.product_tmpl_id.uom_id):
                raise ValidationError(
                    "The Unit of Measure '%s' is not compatible with the product base UoM '%s'."
                    % (
                        rec.uom_id.display_name,
                        rec.product_tmpl_id.uom_id.display_name,
                    )
                )


class prod_multi_uom(models.Model):
    _name = 'product.multi.uom.price'
    _inherit = ['pos.load.mixin']
    _description = 'Product variant multiple uom price'

    product_id = fields.Many2one(
        'product.product',
        string='Product variant',
        required=True,
        ondelete="cascade",
        readonly=True
    )
    product_root_parent_path = fields.Char(related='product_id.uom_id.root_parent_path', store=False,)
    uom_id = fields.Many2one('uom.uom',
        string="Unit of Measure",
        domain="[('root_parent_path', '=', product_root_parent_path)]",
        required=True
    )
    price = fields.Float('Price',
        required=True,
        digits='Product Price'
    )



    @api.model
    def _load_pos_data_fields(self, config):
        return ['id', 'product_id', 'uom_id', 'price']

    _product_variant_uom_unique = models.Constraint(
         'UNIQUE(product_id, uom_id)',
         'Each Unit of Measure must be unique per product variant.')

    @api.constrains('uom_id', 'product_id')
    def _check_uom_compatibility(self):
        for rec in self:
            if not rec.uom_id or not rec.product_id.uom_id:
                continue
            if not rec.uom_id._has_common_reference(rec.product_id.uom_id):
                raise ValidationError(
                    "The Unit of Measure '%s' is not compatible with the variant base UoM '%s'."
                    % (
                        rec.uom_id.display_name,
                        rec.product_id.uom_id.display_name,
                    )
                )
