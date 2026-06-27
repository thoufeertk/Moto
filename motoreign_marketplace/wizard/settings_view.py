# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
from odoo import fields, models


class SettingsView(models.TransientModel):
    """Read-only display of default seller payment settings"""
    _name = 'settings.view'
    _description = "Settings View"

    commission = fields.Float(readonly=True, string="Commission (%)")
    amt_limit = fields.Integer(readonly=True, string="Amount Limit")
    minimum_gap = fields.Integer(readonly=True, string="Minimum Gap (days)")
