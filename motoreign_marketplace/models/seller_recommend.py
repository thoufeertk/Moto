# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class SellerRecommend(models.Model):
    """Customer recommendations for marketplace sellers"""
    _name = 'seller.recommend'
    _description = 'Seller Recommendation'
    _rec_name = 'partner_id'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    partner_id = fields.Many2one('res.partner', string="Customer",
                                 required=True, help="Customer making the recommendation")
    seller_id = fields.Many2one('res.partner', string="Seller",
                                required=True, help="Seller being recommended")
    recommend = fields.Selection(selection=[('no', 'No'), ('yes', 'Yes')],
                                 default='no', tracking=True)
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    state = fields.Selection(
        selection=[('unpublished', 'Unpublished'), ('published', 'Published')],
        string='Status', default='unpublished', tracking=True)

    @api.model
    def recommend_func(self, vals):
        """Create or update a seller recommendation"""
        check = self.search([
            ('seller_id', '=', int(vals['seller_id'])),
            ('partner_id', '=', int(vals.get('partner_id', vals.get('customer_id', 0))))
        ])
        if check:
            check.write({'recommend': vals['recommend']})
        else:
            return super(SellerRecommend, self).create(vals)

    def action_publish(self):
        self.write({'state': 'published'})

    def action_unpublish(self):
        self.write({'state': 'unpublished'})
