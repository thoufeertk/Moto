# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import fields, models


class HelpfulInfo(models.Model):
    """Stores whether a customer found a seller review helpful"""
    _name = 'helpful.info'
    _description = "Helpful Info"

    customer_id = fields.Many2one('res.partner', string='Customer', help='Customer')
    msg = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                           string='Was this review helpful?', help='Response')
    review_id = fields.Many2one('seller.review', string='Review', help='Review')
