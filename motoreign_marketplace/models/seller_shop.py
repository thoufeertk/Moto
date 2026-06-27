# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import fields, models, _
from odoo.exceptions import UserError


class SellerShop(models.Model):
    """Manages individual seller shops on the marketplace"""
    _name = 'seller.shop'
    _description = "Seller Shop"

    name = fields.Char(string="Name", help="Shop name")
    shop_url = fields.Char(string='Shop Url', required=True,
                           help="URL slug for the shop on the website")
    shop_banner = fields.Char(string="Shop Banner", help="Banner URL for the shop")
    tag_line = fields.Char(string='Tag Line', help="Shop tag line")
    description = fields.Char(string='Description', help="Shop description")
    seller_id = fields.Many2one('res.partner', string='Seller',
                                help="Seller name",
                                default=lambda self: self.env.user.partner_id.id,
                                domain=[('state', '=', 'Approved')])
    seller_image = fields.Binary(related='seller_id.image_1920',
                                 string="Seller Image", help="Seller image")
    address = fields.Text(string='Address', help="Shop address")
    phone = fields.Char(string='Phone', help="Phone number")
    mobile_number = fields.Char(string='Mobile Number', help="Mobile number")
    email = fields.Char(string='E-mail', help="Email address")
    fax = fields.Char(string='Fax', help="Fax number")
    is_publish = fields.Boolean(string="Is Published",
                                help="Whether this shop is published on the website")
    product_count = fields.Integer(string='Product Count',
                                   help="Total products in the shop")
    product_ids = fields.Many2many('product.template', string="Products",
                                   help="Products in the shop")
    state = fields.Selection(
        selection=[('Pending for Approval', 'Pending for Approval'),
                   ('Approved', 'Approved'),
                   ('Denied', 'Denied')],
        string="State", help="Shop approval state",
        default="Pending for Approval")

    def approve_request(self):
        """Approve the seller shop request"""
        self.state = 'Approved'

    def reject_request(self):
        """Reject the seller shop request"""
        self.state = 'Denied'

    def action_toggle_is_published(self):
        """Toggle shop published state; only approved shops can be published"""
        if self.state == 'Approved':
            self.is_publish = not self.is_publish
        else:
            raise UserError(_("You can only publish approved shops."))
