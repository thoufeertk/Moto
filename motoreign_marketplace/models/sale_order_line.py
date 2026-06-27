# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import fields, models


class SaleOrderLine(models.Model):
    """Extends sale order line with seller and marketplace state"""
    _inherit = 'sale.order.line'

    seller_id = fields.Many2one('res.partner', string="Seller", readonly=True,
                                related='product_id.seller_id',
                                help="Seller of this product")
    partner_id = fields.Many2one('res.partner', related='order_id.partner_id',
                                 string="Customer", help="Customer on this order")
    state = fields.Selection(
        selection=[('pending', 'Pending'), ('approved', 'Approved'),
                   ('shipped', 'Shipped'), ('cancel', 'Cancelled')],
        string="Fulfilment State", help="Seller-side fulfilment state")

    def cancel_order(self):
        """Cancel this order line"""
        self.state = 'cancel'

    def approve_order(self):
        """Approve and create a dedicated delivery for this line"""
        existing = self.env['stock.picking'].sudo().search(
            [('origin', '=', self.order_id.name)], limit=1)
        partner_id = existing.partner_id
        picking_type = existing.picking_type_id
        location_id = existing.location_id
        location_dest_id = existing.location_dest_id

        qty_quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', location_id.id)
        ], limit=1)
        forecast = (qty_quant.quantity
                    if qty_quant and qty_quant.quantity > self.product_uom_qty
                    else self.product_uom_qty)

        move_vals = [(0, 0, {
            'product_id': self.product_id.id,
            'product_uom_qty': self.product_uom_qty,
            'forecast_availability': forecast,
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'name': existing.name or self.order_id.name,
        })]

        if existing and existing.state != 'cancel':
            existing.state = 'cancel'

        new_pick = self.env['stock.picking'].create({
            'partner_id': partner_id.id,
            'picking_type_id': picking_type.id,
            'seller_id': self.seller_id.id,
            'move_ids_without_package': move_vals,
            'origin': self.order_id.name,
        })
        new_pick.ref_id = self.id
        new_pick.state = 'assigned'
        self.state = 'approved'

    def shipped(self):
        """Open the delivery (stock.picking) for this order line"""
        picking = self.env['stock.picking'].search([('ref_id', '=', self.id)], limit=1)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Delivery',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'res_id': picking.id,
        }
