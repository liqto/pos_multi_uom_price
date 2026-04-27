/** © 2026 ehuerta _at_ ixer.mx
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
 */

import { Orderline } from "@point_of_sale/app/components/orderline/orderline";
import { patch } from "@web/core/utils/patch";

patch(Orderline.prototype, {
    get lineScreenValues() {
        const values = super.lineScreenValues;
        if (!values || !this.line) {
            return values;
        }
        const line = this.line;
        values.displayPriceUnit =
            values.displayPriceUnit &&
            `${line.currencyDisplayPriceUnit} / ${line.product_uom_id?.name || ""}`;

        return values;
    },	    
});
