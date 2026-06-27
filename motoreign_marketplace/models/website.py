# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import fields, models


class WebSite(models.Model):
    """Extends website to store seller marketplace banner"""
    _inherit = 'website'

    seller_banner = fields.Binary(
        string="Seller Banner",
        help="Banner displayed on the marketplace landing page")
