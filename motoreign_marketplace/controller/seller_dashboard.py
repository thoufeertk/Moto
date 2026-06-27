# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
from odoo import http
from odoo.http import request


class SellerDashboard(http.Controller):
    """JSON endpoint powering the seller/admin dashboard widget"""

    @http.route(['/seller_dashboard'], type='json', auth="user", website=True)
    def seller_dashboard(self):
        """Return counts for all dashboard tiles"""
        env = request.env
        return {
            'pending': env['product.template'].search_count([('state', '=', 'pending')]),
            'approved': env['product.template'].search_count([('state', '=', 'approved')]),
            'rejected': env['product.template'].search_count([('state', '=', 'rejected')]),
            'user_type': env['res.users'].has_group(
                'motoreign_marketplace.motoreign_marketplace_admin'),
            'seller_pending': env['res.partner'].search_count(
                [('state', '=', 'Pending for Approval')]),
            'seller_approved': env['res.partner'].search_count([('state', '=', 'Approved')]),
            'seller_rejected': env['res.partner'].search_count([('state', '=', 'Denied')]),
            'inventory_pending': env['inventory.request'].search_count(
                [('state', '=', 'Requested')]),
            'inventory_approved': env['inventory.request'].search_count(
                [('state', '=', 'Approved')]),
            'inventory_rejected': env['inventory.request'].search_count(
                [('state', '=', 'Rejected')]),
            'payment_pending': env['seller.payment'].search_count(
                [('state', '=', 'Requested')]),
            'payment_approved': env['seller.payment'].search_count(
                [('state', '=', 'Validated')]),
            'payment_rejected': env['seller.payment'].search_count(
                [('state', '=', 'Rejected')]),
            'order_pending': env['sale.order.line'].search_count(
                [('state', '=', 'pending')]),
            'order_approved': env['sale.order.line'].search_count(
                [('state', '=', 'approved')]),
            'order_shipped': env['sale.order.line'].search_count(
                [('state', '=', 'shipped')]),
            'order_cancel': env['sale.order.line'].search_count(
                [('state', '=', 'cancel')]),
            'sale_order_kanban_id': env['ir.ui.view'].search(
                [('name', '=', 'multi.vendor.sale.order.line.kanban')]).id,
            'product_kanban_id': env['ir.ui.view'].search(
                [('name', '=', 'multi.vendor.view.kanban')]).id,
            'sale_order_form_id': env['ir.ui.view'].search(
                [('name', '=', 'multi.vendor.sale.order.line.form.readonly')]).id,
        }
