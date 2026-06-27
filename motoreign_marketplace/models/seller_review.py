# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class SellerReview(models.Model):
    """Customer reviews for marketplace sellers"""
    _name = 'seller.review'
    _description = 'Seller Review'
    _rec_name = 'review_title'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    seller_id = fields.Many2one('res.partner', string="Seller",
                                required=True, help="Seller being reviewed")
    customer_id = fields.Many2one('res.partner', string="Customer",
                                  required=True, help="Reviewer")
    customer_email = fields.Char(related='customer_id.email', string="Email",
                                 help="Customer email")
    rating = fields.Float(string="Rating", required=True,
                          help="Rating between 0 and 5")
    review_title = fields.Char(string="Review Title", help="Short title for the review")
    date = fields.Date(string="Date", default=fields.Date.today,
                       help="Review date")
    message = fields.Text(string="Message", help="Review text", size=150)
    like_count = fields.Integer(string='Helpful Count',
                                compute='_compute_count', help="Positive votes")
    unlike_count = fields.Integer(string='Not Helpful Count',
                                  compute='_compute_count', help="Negative votes")
    state = fields.Selection(
        selection=[('unpublished', 'Unpublished'), ('published', 'Published')],
        string='Status', default='unpublished', tracking=True)
    help_info_ids = fields.One2many('helpful.info', 'review_id',
                                    string="Helpful Info")

    _sql_constraints = [
        ('rating_range', 'check(rating >= 0 and rating <= 5)',
         'Rating must be between 0 and 5')
    ]

    @api.model
    def rate_review(self, vals):
        """Create or update a seller review"""
        check = self.sudo().search([
            ('seller_id', '=', int(vals['seller_id'])),
            ('customer_id', '=', int(vals['customer_id']))
        ])
        auto_publish = self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.auto_publish_seller_review')
        if check:
            check.sudo().write({'rating': vals['rating'], 'message': vals['message']})
            if auto_publish:
                check.sudo().action_publish()
            else:
                check.sudo().action_unpublish()
        else:
            rec = super(SellerReview, self).sudo().create(vals)
            if auto_publish:
                rec.action_publish()
            return rec

    def action_publish(self):
        """Publish the review"""
        self.state = 'published'

    def action_unpublish(self):
        """Unpublish the review"""
        self.state = 'unpublished'

    def _compute_count(self):
        """Compute helpful / not-helpful vote counts"""
        for record in self:
            record.like_count = self.env['helpful.info'].search_count(
                [('msg', '=', 'yes'), ('review_id', '=', record.id)])
            record.unlike_count = self.env['helpful.info'].search_count(
                [('msg', '=', 'no'), ('review_id', '=', record.id)])
