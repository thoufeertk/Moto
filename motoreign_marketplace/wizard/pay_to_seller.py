# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
from odoo import fields, models


class PayToSeller(models.TransientModel):
    """Wizard for admin to pay a seller their earned commission"""
    _name = 'pay.to.seller'
    _description = "Pay To Seller"

    date = fields.Date(string='Date', required=True, default=fields.Date.today,
                       help='Payment date')
    seller_id = fields.Many2one('res.partner', string='Seller', required=True)
    cashable_amount = fields.Float(string='Cashable Amount',
                                   related='seller_id.total_commission', readonly=True)
    payment_amount = fields.Float(string='Payment Amount')
    payment_mode = fields.Selection([('cash', 'Cash'), ('bank', 'Bank')],
                                    string='Payment Mode')
    payment_methods_id = fields.Many2one('account.payment.method.line',
                                         string='Payment Method')
    memo = fields.Char(string='Memo', required=True)
    payment_description = fields.Text(string='Payment Description', required=True)
