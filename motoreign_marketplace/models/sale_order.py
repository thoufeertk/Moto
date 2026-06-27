# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class SaleOrder(models.Model):
    """Extends sale order with marketplace seller and commission logic"""
    _inherit = 'sale.order'

    product_id = fields.Many2one('product.template', string="Product",
                                 help="Primary product on this order")
    seller_id = fields.Many2one('res.partner', readonly=True,
                                string="Seller",
                                related='product_id.seller_id')
    quantity = fields.Float(related='order_line.product_uom_qty',
                            string="Quantity", readonly=False)
    qty_delivered = fields.Float(related='order_line.qty_delivered',
                                 string="Delivered Qty", readonly=False)
    # Extend state with marketplace states without breaking existing onchanges
    state = fields.Selection(selection_add=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
    ])
    unit_price = fields.Float(related='order_line.price_unit',
                              string="Unit Price", readonly=False)
    discount = fields.Float(related='order_line.discount',
                            string="Discount", readonly=False)
    subtotal = fields.Monetary(related='order_line.price_subtotal',
                               string="Subtotal", readonly=False)
    description = fields.Text(string="Description", help="Product description")

    def action_confirm(self):
        """On confirm, set to pending and calculate seller commission"""
        res = super().action_confirm()
        self.state = 'pending'
        for line in self.order_line:
            seller = line.product_id.seller_id
            if not seller:
                continue
            commission_rate = (seller.default_commission or float(
                self.env['ir.config_parameter'].sudo().get_param(
                    'motoreign_marketplace.commission') or 0))
            seller.total_commission += line.price_subtotal * (commission_rate / 100)
        return res
