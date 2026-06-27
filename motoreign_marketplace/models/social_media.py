# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import fields, models


class SocialMedia(models.Model):
    """Social media platforms for seller profiles"""
    _name = 'social.media'
    _description = "Social Media"

    name = fields.Char(string="Name", help="Platform name", required=True)
    icon = fields.Binary(string="Icon", help="Platform icon")
    base_url = fields.Char(string="Base Url", help="Base URL of the social media platform", required=True)
