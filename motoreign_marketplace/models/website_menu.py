# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import models


class WebsiteMenu(models.Model):
    """Controls visibility of the Sell menu based on backend settings"""
    _inherit = "website.menu"

    def _compute_visible(self):
        super()._compute_visible()
        show_sell_menu_header = self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.show_sell_menu_header')
        for menu in self:
            if menu.url == '/sell':
                menu.is_visible = bool(show_sell_menu_header)
