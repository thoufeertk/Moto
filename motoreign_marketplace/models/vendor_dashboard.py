# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import fields, models


class VendorDashboard(models.Model):
    """Vendor dashboard model"""
    _name = 'vendor.dashboard'
    _description = "Vendor Dashboard"

    sample = fields.Boolean(string='Sample', help='Sample dashboard field')
