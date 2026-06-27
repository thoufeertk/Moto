# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RequestPayment(models.TransientModel):
    """Wizard for sellers to request payment against earned commission"""
    _name = 'request.payment'
    _description = "Request Payment"

    seller_id = fields.Many2one('res.partner', string='Seller', required=True,
                                default=lambda self: self.env.user.partner_id.id,
                                help='Seller')
    cashable_amount = fields.Float(string='Available Commission',
                                   help='Total commission available',
                                   readonly=True)
    request_amount = fields.Float(string='Requested Amount', required=True,
                                  help='Amount being requested')
    payment_description = fields.Text(string='Payment Description', required=True,
                                      help='Reason for the payment request')

    @api.onchange('seller_id')
    def _onchange_seller_id(self):
        """Update available commission when seller changes"""
        if self.seller_id:
            self.cashable_amount = self.seller_id.total_commission

    def request_payment(self):
        """Validate limits then create a seller.payment record"""
        amount_limit = int(self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.amt_limit') or 0)
        min_gap = int(self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.min_gap') or 0)
        partner = self.seller_id
        today = fields.Date.today()
        min_date = fields.Date.subtract(today, days=min_gap)
        recent = self.env['seller.payment'].search([
            ('seller_id', '=', partner.id),
            ('state', '=', 'Validated'),
            ('date', '>=', min_date),
        ], limit=1)
        if (self.request_amount > partner.total_commission
                or (amount_limit and self.request_amount > amount_limit)
                or recent):
            raise ValidationError(_(
                "Amount exceeds your commission balance, the configured limit "
                "(%s), or the minimum gap of %s days has not passed."
            ) % (amount_limit, min_gap))
        self.env['seller.payment'].create({
            'seller_id': partner.id,
            'payment_mode': 'Cash',
            'commission': partner.total_commission,
            'payable_amount': self.request_amount,
            'date': today,
            'type_id': 1,
            'memo': self.payment_description,
            'state': 'Requested',
        })
