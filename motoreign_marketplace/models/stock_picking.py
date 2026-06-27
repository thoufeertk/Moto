# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import fields, models


class StockPicking(models.Model):
    """Extends stock picking with seller and order line reference"""
    _inherit = 'stock.picking'

    seller_id = fields.Many2one('res.partner', string="Seller",
                                help="Seller responsible for this delivery")
    ref_id = fields.Integer(string="Order Line Ref",
                            help="Reference to the sale order line")

    def button_validate(self):
        """On validate, update the sale order line qty_delivered and state"""
        res = super().button_validate()
        if self.ref_id:
            sale_line = self.env['sale.order.line'].sudo().search(
                [('id', '=', self.ref_id)], limit=1)
            if sale_line:
                delivered = sum(self.move_ids_without_package.mapped('quantity'))
                sale_line.write({'state': 'shipped', 'qty_delivered': delivered})
        return res
