/** © 2026 ehuerta _at_ ixer.mx
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
 */

import { PosOrderline } from "@point_of_sale/app/models/pos_order_line";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";
import { localization as l10n } from "@web/core/l10n/localization";
import { formatFloat, roundPrecision } from "@web/core/utils/numbers";


patch(PosOrderline.prototype, {
    setup(vals) {
        super.setup(vals);
        this.product_uom_id = this.product_uom_id || this.product_id.uom_id;
    }, 
     set_uom(uom_id) {
        this.product_uom_id = uom_id;
    },
    get quantityStr() {
        let unitPart = "";
        let decimalPart = "";
        const unit = this.product_uom_id;       
        const decimalPoint = l10n.decimalPoint;

        if (unit) {
            if (unit.rounding) {
                const ProductUnit = this.models["decimal.precision"].find(
                    (dp) => dp.name === "Product Unit"
                );

                if (this.qty % 1 === 0) {
                    unitPart = this.qty.toFixed(0);
                } else {
                    const formatted = formatFloat(this.qty, { digits: [69, ProductUnit.digits] });
                    const parts = formatted.split(decimalPoint);
                    unitPart = parts[0];
                    decimalPart = parts[1] || "";
                }
            } else {
                unitPart = this.qty.toFixed(0);
            }
        } else {
            unitPart = "" + this.qty;
        }
        return {
            qtyStr: unitPart + (decimalPart ? decimalPoint + decimalPart : ""),
            unitPart: unitPart,
            decimalPoint: decimalPoint,
            decimalPart: decimalPart,
        };
    },	
    getUnit() {
        return this.product_uom_id;
    },       
    isPosGroupable() {
        const unit_groupable = this.product_uom_id
            ? this.product_uom_id.is_pos_groupable
            : false;
        return unit_groupable && !this.isPartOfCombo();
    },
    setQuantity(quantity, keep_price) {
        this.uiState.oldQty = this.qty;
        if (this.order_id.preset_id?.is_return) {
            quantity = -Math.abs(quantity);
        }

        this.order_id.assertEditable();
        const quant =
            typeof quantity === "number" ? quantity : parseFloat("" + (quantity ? quantity : 0));

        const allLineToRefundUuids = this.models["pos.order"].reduce((acc, order) => {
            Object.assign(acc, order.uiState.lineToRefund);
            return acc;
        }, {});

        if (this.refunded_orderline_id?.uuid in allLineToRefundUuids) {
            const refundDetails = allLineToRefundUuids[this.refunded_orderline_id.uuid];
            const maxQtyToRefund = refundDetails.line.qty - refundDetails.line.refundedQty;
            if (quant > 0) {
                return {
                    title: _t("Positive quantity not allowed"),
                    body: _t(
                        "Only a negative quantity is allowed for this refund line. Click on +/- to modify the quantity to be refunded."
                    ),
                };
            } else if (quant == 0) {
                refundDetails.qty = 0;
            } else if (-quant <= maxQtyToRefund) {
                refundDetails.qty = -quant;
            } else {
                return {
                    title: _t("Greater than allowed"),
                    body: _t(
                        "The requested quantity to be refunded is higher than the refundable quantity."
                    ),
                };
            }
        }

        const rounder =
            this.product_uom_id ||
            this.models["decimal.precision"].find((dp) => dp.name === "Product Unit");

        this.qty = rounder.round(quant);

        // just like in sale.order changing the qty will recompute the unit price
        if (!keep_price && this.price_type === "original") {
            const productTemplate = this.product_id.product_tmpl_id;
            if (this.isLotTracked()) {
                const related_lines = [];
                const price = productTemplate.getPrice(
                    this.order_id.pricelist_id,
                    this.getQuantity(),
                    this.getPriceExtra(),
                    false,
                    this.product_id,
                    this,
                    related_lines
                );
                related_lines.forEach((line) => line.setUnitPrice(price));
            } else {
                this.setUnitPrice(
                    productTemplate.getPrice(
                        this.order_id.pricelist_id,
                        this.getQuantity(),
                        this.getPriceExtra(),
                        false,
                        this.product_id
                    )
                );
            }
        }
        for (const comboLine of this.combo_line_ids) {
            // If each combo contains 2 qty of a product, we wanna keep this ratio after setting the new quantity on the parent product.
            comboLine.setQuantity((comboLine.qty / this.uiState.oldQty || 1) * quantity, true);
        }
        return true;
    }

});
