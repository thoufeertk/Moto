# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class InventoryRequest(models.Model):
    """Seller requests to add stock quantity for a product"""
    _name = 'inventory.request'
    _description = "Inventory Request"

    name = fields.Char(string='Title', required=True, help='Request title')
    product_id = fields.Many2one('product.template', string='Product',
                                 required=True, help='Product')
    seller_id = fields.Many2one(related='product_id.seller_id',
                                string='Seller', help='Seller')
    qty_new = fields.Integer(string='New Quantity', required=True,
                             help='New quantity to add to stock')
    location_id = fields.Many2one('stock.location', string='Location',
                                  required=True, help='Stock location')
    date = fields.Datetime(string='Created Date', default=fields.Datetime.now,
                           help='Request creation date')
    note = fields.Text(string='Note', help='Additional notes')
    state = fields.Selection(
        selection=[('Draft', 'Draft'), ('Requested', 'Requested'),
                   ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        string='Status', group_expand='_group_expand_states',
        default='Draft', readonly=True)

    @api.onchange('name')
    def _onchange_name(self):
        """Pre-fill location from settings"""
        location_id = self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.seller_location_id')
        if location_id:
            self.location_id = self.env['stock.location'].browse(int(location_id))

    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def approve_request(self):
        """Approve and apply inventory adjustment"""
        self.state = 'Approved'
        product_tmpl = self.env['product.template'].browse(self.product_id.id)
        product = self.env['product.product'].search(
            [('product_tmpl_id', '=', product_tmpl.id)], limit=1)
        if product:
            new_qty = product_tmpl.qty_available + self.qty_new
            self.env['stock.quant'].with_context(inventory_mode=True).create({
                'product_id': product.id,
                'inventory_quantity': new_qty,
                'location_id': self.location_id.id,
            }).action_apply_inventory()

    def reject_request(self):
        """Reject the inventory request"""
        self.state = 'Rejected'

    def request(self):
        """Submit the request; auto-approve if setting enabled"""
        if self.env['ir.config_parameter'].sudo().get_param(
                'motoreign_marketplace.quantity_approval'):
            self.approve_request()
        else:
            self.state = 'Requested'
