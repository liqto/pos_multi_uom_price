/** © 2026 ehuerta _at_ ixer.mx
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).
 */

import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";
import { patch } from "@web/core/utils/patch";
import { SelectionPopup } from "@point_of_sale/app/components/popups/selection_popup/selection_popup";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";


patch(ControlButtons.prototype, {
    async onClickUOMSelector() {
	const selectedLine = this.pos.getOrder().getSelectedOrderline();
    if (!selectedLine) {
        this.dialog.add(AlertDialog, {
            title: _t("No product"),
            body: _t("Select a product line first."),
        });
        return;
    }

    const records = this.pos.models["product.multi.uom.price"]
        .filter(rec => rec.product_id.id === selectedLine.product_id.id);

    if (!records.length) {
        return;
    }

    let uom_price = null;
    uom_price = await makeAwaitable(this.dialog, SelectionPopup, {
        title: _t("UOM"),
        list: records.map((rec) => (
            {id: rec.uom_id.id,
             label: rec.uom_id.name,
             item: rec,
             isSelected: true,
             }))
    });
    if (uom_price){
        selectedLine.setUnitPrice(uom_price.price);
        selectedLine.price_type = "manual";
        selectedLine.set_uom(uom_price.uom_id)
    }

    },
});
