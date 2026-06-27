/** @odoo-module **/
// Motoreign Multi Vendor Marketplace - Odoo 19
// Seller Dashboard OWL Component

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

class SellerDashboard extends Component {
    static template = "motoreign_marketplace.SellerDashboard";
    static props = {};

    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.state = useState({
            pending: 0, approved: 0, rejected: 0,
            user_type: false,
            seller_pending: 0, seller_approved: 0, seller_rejected: 0,
            inventory_pending: 0, inventory_approved: 0, inventory_rejected: 0,
            payment_pending: 0, payment_approved: 0, payment_rejected: 0,
            order_pending: 0, order_approved: 0, order_shipped: 0, order_cancel: 0,
            sale_order_kanban_id: false, product_kanban_id: false, sale_order_form_id: false,
        });
        onWillStart(async () => {
            const data = await this.rpc("/seller_dashboard", {});
            Object.assign(this.state, data);
        });
    }

    openView(model, viewType, domain, viewId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            view_mode: viewType,
            views: [[viewId || false, viewType]],
            domain: domain || [],
            target: "current",
        });
    }

    openProducts(state) {
        this.openView("product.template", "kanban",
            [["state", "=", state]], this.state.product_kanban_id);
    }

    openOrders(state) {
        this.openView("sale.order.line", "kanban",
            [["state", "=", state]], this.state.sale_order_kanban_id);
    }

    openSellers(state) {
        this.openView("res.partner", "list", [["state", "=", state]]);
    }

    openInventory(state) {
        this.openView("inventory.request", "list", [["state", "=", state]]);
    }

    openPayments(state) {
        this.openView("seller.payment", "list", [["state", "=", state]]);
    }
}

registry.category("actions").add("motoreign_marketplace.seller_dashboard_action", SellerDashboard);
