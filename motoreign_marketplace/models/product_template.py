# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class ProductTemplate(models.Model):
    """Extends product.template with seller assignment and approval workflow"""
    _inherit = "product.template"

    website_category_id = fields.Many2one('product.public.category', string='Website Category')
    cmpy_email = fields.Text(default=lambda self: self.env.company.email, string='Company Email')
    seller_id = fields.Many2one('res.partner', string='Seller',
                                default=lambda self: self.env.user.partner_id.id,
                                domain=[('state', '=', 'Approved')])
    seller_pic = fields.Binary(related='seller_id.image_1920', string='Seller Image')
    web = fields.Many2one("website", string="Website")
    alt_pro_id = fields.Many2one("product.template", string="Alternative Products")
    acc_pro_id = fields.Many2one("product.template", string="Accessory Products")
    forecasted_qty = fields.Integer(string='Forecasted Quantity')
    initial_qty = fields.Integer(string='Initial Quantity')
    state = fields.Selection([
        ('draft', 'Draft'), ('pending', 'Pending'),
        ('approved', 'Approved'), ('rejected', 'Rejected'),
    ], string='Product Status', default='draft', readonly=True,
       tracking=True, group_expand='_group_expand_states')
    item_ids = fields.One2many('multi.vendor.pricelist', 'product_inv_id', string='Pricelist Items')
    product_price_setting = fields.Boolean(string='Show Product Price')
    product_variants_setting = fields.Boolean(string='Allow Variants')
    product_uom = fields.Boolean(string='Show UoM')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        categ_id = self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.internal_categ_id')
        if categ_id:
            res.categ_id = int(categ_id)
        return res

    def write(self, vals):
        res = super().write(vals)
        for line in self.item_ids:
            existing = self.env['product.pricelist.item'].search([
                ('pricelist_id', '=', line.price_list_id.id),
                ('pricelist_multivendor_id', '=', line._origin.id),
            ], limit=1)
            item_vals = {
                'product_tmpl_id': self._origin.id,
                'min_quantity': line.min_qty,
                'fixed_price': line.price_of_pricelist,
                'date_start': line.start_date,
                'date_end': line.end_date,
            }
            if existing:
                existing.write(item_vals)
            else:
                item_vals['pricelist_multivendor_id'] = line._origin.id
                line.price_list_id.write({'item_ids': [(0, 0, item_vals)]})
        return res

    def send_product_status_mail(self):
        """Send email on product approval/rejection"""
        params = self.env['res.config.settings'].search([], order='create_date desc', limit=1)
        if params.product_approve_admin_mail and params.product_approve_admin_mail_template_id:
            params.product_approve_admin_mail_template_id.send_mail(self.id, force_send=True)
        if params.product_approve_seller_mail and params.product_approve_seller_mail_template_id:
            params.product_approve_seller_mail_template_id.send_mail(self.id, force_send=True)

    def change_state_approved(self):
        """Admin approves a product"""
        self.state = 'approved'
        config = self.env['ir.config_parameter'].sudo()
        self.product_price_setting = bool(config.get_param('motoreign_marketplace.product_pricing'))
        self.product_variants_setting = bool(config.get_param('motoreign_marketplace.product_variants'))
        self.product_uom = bool(config.get_param('motoreign_marketplace.uom'))
        self.send_product_status_mail()

    @api.onchange('name')
    def _onchange_name(self):
        """Set internal category from settings when product name changes"""
        categ_id = self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.internal_categ_id')
        if categ_id:
            self.categ_id = self.env['product.category'].browse(int(categ_id))

    def change_state_pending(self):
        """Seller submits product for approval"""
        if self.env['ir.config_parameter'].sudo().get_param(
                'motoreign_marketplace.product_approval'):
            self.state = 'approved'
        else:
            self.state = 'pending'
        self.sudo().send_product_status_mail()

    def change_state_reject(self):
        """Admin rejects a product"""
        self.state = 'rejected'
        self.send_product_status_mail()

    def toggle_website_published(self):
        self.is_published = not self.is_published

    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]
