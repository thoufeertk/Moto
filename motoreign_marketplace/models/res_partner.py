# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class ResPartner(models.Model):
    """Extends res.partner with seller profile, commission and state"""
    _inherit = 'res.partner'

    profile_url = fields.Char(string='Profile Url', help="Seller profile URL on the website")
    allow_product_variant = fields.Boolean(string='Allow Product Variant')
    payment_method_ids = fields.Many2many('account.payment.method', string="Payment Methods")
    total_amount = fields.Float(string='Total Amount', help="Total sales amount")
    balance_amount = fields.Float(string='Balance Amount', help="Balance amount for seller")
    paid_amount = fields.Float(string='Paid Amount', help="Total paid amount")
    market_place_currency = fields.Monetary(string="Marketplace Currency")
    currency_id = fields.Many2one(
        "res.currency", string="Currency", readonly=True,
        default=lambda self: self.env['res.currency'].search([('name', '=', 'USD')], limit=1).id)
    return_policy = fields.Html(string='Return Policy')
    shipping_policy = fields.Html(string='Shipping Policy')
    profile_image = fields.Binary(string='Profile Image')
    profile_banner = fields.Binary(string='Profile Banner')
    profile_message = fields.Html(string="Profile Message")
    sale_count = fields.Integer(compute='_compute_sale_count', string="Sale Count")
    amount_available = fields.Float(compute='_compute_amount_available', string="Amount Available")
    avg_rating = fields.Float(compute='_compute_avg_rating', string="Average Rating")
    recommend_count = fields.Float(compute='_compute_recommend_count', string="Recommendation Count")
    is_publish = fields.Boolean(string="Is Published")
    seller_shop_id = fields.Many2one('seller.shop', string="Seller Shop",
                                     domain="[('seller_id', '=', id)]")
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('Pending for Approval', 'Pending for Approval'),
            ('Approved', 'Approved'),
            ('Denied', 'Denied'),
        ],
        default='new', string='Seller Status', tracking=True,
        group_expand='_group_expand_states')
    default_commission = fields.Float(string='Default Sale Commission (%)')
    amount_limit = fields.Float(string='Amount Limit')
    min_gap = fields.Integer(string='Minimum Gap (days)')
    auto_product_approve = fields.Boolean(string="Auto Product Approve")
    auto_quality_approve = fields.Boolean(string="Auto Quality Approve")
    location_id = fields.Many2one('stock.location', string='Default Location')
    warehouse_id = fields.Many2one('stock.warehouse', string='Default Warehouse')
    total_commission = fields.Float(string="Total Commission")
    commission = fields.Float(string="Commission")
    profile_url_value = fields.Char(string='Profile Url Value')

    def req_approve(self):
        """Seller requests approval to sell"""
        if self.env['ir.config_parameter'].sudo().get_param(
                'motoreign_marketplace.seller_approval'):
            self.sudo().approve_seller()
            self.state = 'Approved'
        else:
            self.state = 'Pending for Approval'

    def user_my_profile(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Profile',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.env.user.partner_id.id,
            'target': 'new',
        }

    def new_user_my_profile(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Profile',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.env.user.partner_id.id,
        }

    def action_toggle_published(self):
        """Toggle seller visibility on website seller list"""
        self.is_published = not self.is_published

    def view_settings(self):
        params = self.env['ir.config_parameter'].sudo()
        return {
            'name': 'Default Settings',
            'res_model': 'settings.view',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_commission': params.get_param('motoreign_marketplace.commission'),
                'default_amt_limit': params.get_param('motoreign_marketplace.amt_limit'),
                'default_minimum_gap': params.get_param('motoreign_marketplace.min_gap'),
            },
        }

    def approve(self):
        self.state = 'Approved'

    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    def register_payment(self):
        return {
            'name': 'Payment Request',
            'res_model': 'request.payment',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
        }

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        params = self.env['res.config.settings'].search([], order='create_date desc', limit=1)
        for rec in result:
            if params.seller_request_admin_mail and params.seller_request_admin_mail_template_id:
                params.seller_request_admin_mail_template_id.sudo().send_mail(rec.id, force_send=True)
            if params.seller_request_seller_mail and params.seller_request_seller_mail_template_id:
                params.seller_request_seller_mail_template_id.sudo().send_mail(rec.id, force_send=True)
        return result

    def send_seller_status_mail(self):
        """Send email on seller approval/rejection"""
        params = self.env['res.config.settings'].sudo().search(
            [], order='create_date desc', limit=1)
        if params.seller_approve_admin_mail and params.seller_approve_admin_mail_template_id:
            params.seller_approve_admin_mail_template_id.sudo().send_mail(self.id, force_send=True)
        if params.seller_approve_seller_mail and params.seller_approve_seller_mail_template_id:
            params.seller_approve_seller_mail_template_id.sudo().send_mail(self.id, force_send=True)

    def approve_seller(self):
        """Grant seller group access and move to Approved state"""
        user = self.env['res.users'].search([('partner_id', '=', self.id)], limit=1)
        if not user:
            return
        seller_group = self.env.ref('motoreign_marketplace.motoreign_marketplace_seller')
        internal_group = self.env.ref('base.group_user')
        stock_group = self.env.ref('stock.group_stock_user')
        sale_group = self.env.ref('sales_team.group_sale_manager')
        user.sudo().write({'group_ids': [(6, 0, [
            internal_group.id, seller_group.id, stock_group.id, sale_group.id
        ])]})
        # Remove salesman sub-groups to avoid conflicts
        for gref in ('sales_team.group_sale_salesman', 'sales_team.group_sale_salesman_all_leads'):
            grp = self.env.ref(gref)
            if user in grp.users:
                grp.write({'users': [(3, user.id, 0)]})
        if self.state == 'Pending for Approval':
            self.state = 'Approved'
            self.send_seller_status_mail()

    def reject_seller(self):
        self.state = 'Denied'
        self.send_seller_status_mail()

    def create_shop(self):
        return {
            'name': 'Seller Shop',
            'res_model': 'seller.shop',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
        }

    def _compute_sale_count(self):
        for rec in self:
            rec.sale_count = self.env['sale.order.line'].search_count(
                [('seller_id', '=', rec.id)])

    def _compute_amount_available(self):
        for rec in self:
            rec.amount_available = rec.total_commission

    def view_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Orders',
            'view_mode': 'list,form',
            'res_model': 'sale.order.line',
            'domain': [('seller_id', '=', self.id)],
        }

    def _compute_avg_rating(self):
        for rec in self:
            reviews = self.env['seller.review'].search([('seller_id', '=', rec.id)])
            if reviews:
                rec.avg_rating = sum(r.rating for r in reviews) / len(reviews)
            else:
                rec.avg_rating = 0.0

    def view_rating(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reviews',
            'view_mode': 'list,form',
            'res_model': 'seller.review',
            'domain': [('seller_id', '=', self.id)],
        }

    def _compute_recommend_count(self):
        for rec in self:
            rec.recommend_count = self.env['seller.recommend'].search_count(
                [('seller_id', '=', rec.id), ('recommend', '=', 'yes')])

    def view_recommend(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Recommendations',
            'view_mode': 'list',
            'res_model': 'seller.recommend',
            'domain': [('seller_id', '=', self.id), ('recommend', '=', 'yes')],
        }
