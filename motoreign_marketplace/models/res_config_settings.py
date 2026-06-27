# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    """Marketplace configuration settings"""
    _inherit = 'res.config.settings'

    seller_approval = fields.Boolean(string='Auto Seller Approval',
        config_parameter='motoreign_marketplace.seller_approval')
    quantity_approval = fields.Boolean(string='Auto Quantity Approval',
        config_parameter='motoreign_marketplace.quantity_approval')
    product_approval = fields.Boolean(string='Auto Product Approval',
        config_parameter='motoreign_marketplace.product_approval')
    internal_categ_id = fields.Many2one('product.category',
        string='Internal Category', required=True,
        config_parameter='motoreign_marketplace.internal_categ_id',
        default=lambda self: self.env.ref('product.product_category_all'))
    product_variants = fields.Boolean(string='Allow Product Variants',
        config_parameter='motoreign_marketplace.product_variants')
    product_pricing = fields.Boolean(string='Show Product Price',
        config_parameter='motoreign_marketplace.product_pricing')
    uom = fields.Boolean(string='Show UoM',
        config_parameter='motoreign_marketplace.uom')
    seller_location_id = fields.Many2one('stock.location', string='Seller Location',
        required=True, config_parameter='motoreign_marketplace.seller_location_id',
        default=lambda self: self.env.ref('stock.stock_location_stock'))
    seller_warehouse_id = fields.Many2one('stock.warehouse', string='Seller Warehouse',
        required=True, config_parameter='motoreign_marketplace.seller_warehouse_id',
        default=lambda self: self.env.ref('stock.warehouse0'))
    seller_shop = fields.Boolean(string='Enable Seller Shops',
        config_parameter='motoreign_marketplace.seller_shop')
    commission = fields.Float(string='Global Commission (%)', default=2.0,
        config_parameter='motoreign_marketplace.commission')
    currency = fields.Many2one('res.currency', string='Marketplace Currency',
        required=True, config_parameter='motoreign_marketplace.currency',
        default=lambda self: self.env.company.currency_id)
    amt_limit = fields.Integer(string='Payment Amount Limit',
        config_parameter='motoreign_marketplace.amt_limit')
    min_gap = fields.Integer(string='Minimum Payment Gap (days)',
        config_parameter='motoreign_marketplace.min_gap', default=2)
    pay_journal = fields.Many2one('account.journal', string='Seller Payment Journal',
        config_parameter='motoreign_marketplace.pay_journal',
        default=lambda self: self.env.ref(
            'motoreign_marketplace.seller_payment_journal_creation', raise_if_not_found=False))
    pay_product = fields.Many2one('product.product', string='Payment Product',
        config_parameter='motoreign_marketplace.pay_product',
        default=lambda self: self.env.ref(
            'motoreign_marketplace.seller_payment_product_creation', raise_if_not_found=False))
    seller_request_admin_mail = fields.Boolean(string='Notify Admin on Seller Request',
        config_parameter='motoreign_marketplace.seller_request_admin_mail')
    seller_request_admin_mail_template_id = fields.Many2one('mail.template',
        string='Admin Email Template',
        config_parameter='motoreign_marketplace.seller_request_admin_mail_template_id')
    seller_request_seller_mail = fields.Boolean(string='Notify Seller on Request',
        config_parameter='motoreign_marketplace.seller_request_seller_mail')
    seller_request_seller_mail_template_id = fields.Many2one('mail.template',
        string='Seller Email Template',
        config_parameter='motoreign_marketplace.seller_request_seller_mail_template_id')
    seller_approve_admin_mail = fields.Boolean(string='Notify Admin on Approval',
        config_parameter='motoreign_marketplace.seller_approve_admin_mail')
    seller_approve_admin_mail_template_id = fields.Many2one('mail.template',
        config_parameter='motoreign_marketplace.seller_approve_admin_mail_template_id')
    seller_approve_seller_mail = fields.Boolean(string='Notify Seller on Approval',
        config_parameter='motoreign_marketplace.seller_approve_seller_mail')
    seller_approve_seller_mail_template_id = fields.Many2one('mail.template',
        config_parameter='motoreign_marketplace.seller_approve_seller_mail_template_id')
    product_approve_admin_mail = fields.Boolean(string='Notify Admin on Product Approval',
        config_parameter='motoreign_marketplace.product_approve_admin_mail')
    product_approve_admin_mail_template_id = fields.Many2one('mail.template',
        config_parameter='motoreign_marketplace.product_approve_admin_mail_template_id')
    product_approve_seller_mail = fields.Boolean(string='Notify Seller on Product Approval',
        config_parameter='motoreign_marketplace.product_approve_seller_mail')
    product_approve_seller_mail_template_id = fields.Many2one('mail.template',
        config_parameter='motoreign_marketplace.product_approve_seller_mail_template_id')
    new_order_seller_mail = fields.Boolean(string='Notify Seller on New Order',
        config_parameter='motoreign_marketplace.new_order_admin_mail')
    new_order_seller_mail_template_id = fields.Many2one('mail.template',
        config_parameter='motoreign_marketplace.new_order_admin_mail_template_id')
    prod_count = fields.Boolean(string='Show Product Count on Profile',
        config_parameter='motoreign_marketplace.prod_count')
    sale_count = fields.Boolean(string='Show Sale Count on Profile',
        config_parameter='motoreign_marketplace.sale_count')
    seller_addr = fields.Boolean(string='Show Seller Address',
        config_parameter='motoreign_marketplace.seller_addr')
    seller_since = fields.Boolean(string='Show Seller Since',
        config_parameter='motoreign_marketplace.seller_since')
    ret_policy = fields.Boolean(string='Show Return Policy',
        config_parameter='motoreign_marketplace.ret_policy')
    ship_policy = fields.Boolean(string='Show Shipping Policy',
        config_parameter='motoreign_marketplace.ship_policy')
    shop_tnc = fields.Boolean(string='Show Terms & Conditions',
        config_parameter='motoreign_marketplace.shop_tnc')
    contact_seller_button = fields.Boolean(string='Show Contact Seller Button',
        config_parameter='motoreign_marketplace.contact_seller_button')
    bcome_seller = fields.Boolean(string='Show Become a Seller Button',
        config_parameter='motoreign_marketplace.bcome_seller')
    recent_products = fields.Integer(string='Recent Products Count',
        config_parameter='motoreign_marketplace.recent_products')
    show_seller_review = fields.Boolean(string='Show Seller Reviews',
        config_parameter='motoreign_marketplace.show_seller_review')
    auto_publish_seller_review = fields.Boolean(string='Auto Publish Reviews',
        config_parameter='motoreign_marketplace.auto_publish_seller_review')
    seller_review_count = fields.Integer(string='Reviews to Display',
        config_parameter='motoreign_marketplace.seller_review_count')
    show_sell_menu_header = fields.Boolean(string='Sell Menu in Header',
        config_parameter='motoreign_marketplace.show_sell_menu_header', default=True)
    show_sell_menu_footer = fields.Boolean(string='Sell Menu in Footer',
        config_parameter='motoreign_marketplace.show_sell_menu_footer')
    show_sellers_list = fields.Boolean(string='Show Sellers List',
        config_parameter='motoreign_marketplace.show_sellers_list')
    sell_link_label = fields.Char(string='Sell Link Label',
        config_parameter='motoreign_marketplace.sell_link_label')
    seller_list_link_label = fields.Char(string='Seller List Link Label',
        config_parameter='motoreign_marketplace.seller_list_link_label')
    seller_shop_list_link_label = fields.Char(string='Shop List Link Label',
        config_parameter='motoreign_marketplace.seller_shop_list_link_label')
    new_status_msg = fields.Text(string='New Status Message')
    pending_status_msg = fields.Text(string='Pending Status Message')
    image = fields.Binary(string='Landing Page Banner',
                          related='website_id.seller_banner', readonly=False)
    show_t_and_c = fields.Boolean(string='Show Marketplace T&C',
        config_parameter='motoreign_marketplace.show_t_and_c')

    def set_values(self):
        super().set_values()
        param = self.env['ir.config_parameter'].sudo().set_param
        param('res.config.settings.new_status_msg', self.new_status_msg)
        param('res.config.settings.pending_status_msg', self.pending_status_msg)

    @api.model
    def get_values(self):
        res = super().get_values()
        get = self.env['ir.config_parameter'].sudo().get_param
        res['new_status_msg'] = get('res.config.settings.new_status_msg')
        res['pending_status_msg'] = get('res.config.settings.pending_status_msg')
        return res

    @api.onchange('product_variants')
    def _onchange_product_variants(self):
        for p in self.env['product.template'].search([]):
            p.product_variants_setting = self.product_variants

    @api.onchange('product_pricing')
    def _onchange_product_pricing(self):
        for p in self.env['product.template'].search([]):
            p.product_price_setting = self.product_pricing

    @api.onchange('uom')
    def _onchange_uom(self):
        for p in self.env['product.template'].search([]):
            p.product_uom = self.uom
