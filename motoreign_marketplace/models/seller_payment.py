# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SellerPayment(models.Model):
    """Records of payments made or requested by marketplace sellers"""
    _name = 'seller.payment'
    _description = "Seller Payment"

    name = fields.Char(string='Reference', required=True, readonly=True, default='New',
                       help="Auto-generated sequence reference")
    seller_id = fields.Many2one('res.partner', string='Seller', required=True,
                                default=lambda self: self.env.user.partner_id.id)
    payment_mode = fields.Selection([('Cash', 'Cash'), ('Bank', 'Bank')],
                                    string="Payment Mode", required=True, default='Cash')
    memo = fields.Char(string='Memo', required=True, help="Payment memo")
    payable_amount = fields.Float(string='Payable Amount', required=True)
    date = fields.Date(string='Payment Date', required=True, default=fields.Date.today)
    type_id = fields.Many2one('account.payment.method', string='Type', required=True)
    invoice_cashable = fields.Boolean(string='Invoice Cashable')
    description = fields.Text(string='Description')
    commission = fields.Float(string="Commission", help="Commission earned")
    state = fields.Selection([
        ('Draft', 'Draft'), ('Requested', 'Requested'),
        ('Validated', 'Validated'), ('Rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string="State", default="Draft")

    def request(self):
        """Submit payment request after validating limits"""
        self.state = 'Requested'
        amount_limit = int(self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.amt_limit') or 0)
        min_gap = int(self.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.min_gap') or 0)
        partner = self.seller_id
        today = fields.Date.today()
        min_date = fields.Date.subtract(today, days=min_gap)
        recent = self.env['seller.payment'].search([
            ('seller_id', '=', self.seller_id.id),
            ('state', '=', 'Validated'),
            ('date', '>=', min_date),
        ], limit=1)
        if (self.payable_amount > partner.total_commission
                or (amount_limit and self.payable_amount > amount_limit)
                or recent):
            raise ValidationError(_(
                "Amount exceeds commission balance, the limit (%s), "
                "or minimum gap (%s days) has not passed."
            ) % (amount_limit, min_gap))

    def reject(self):
        self.state = 'Rejected'

    def cancel(self):
        self.state = 'cancelled'

    def validate(self):
        """Validate payment, create vendor bill, deduct from commission"""
        if self.payable_amount > self.seller_id.total_commission:
            raise ValidationError(_("Amount exceeds total commission earned."))

        config = self.env['ir.config_parameter'].sudo()
        product_id = config.get_param('motoreign_marketplace.pay_product')
        journal_id = config.get_param('motoreign_marketplace.pay_journal')
        currency_id = config.get_param('motoreign_marketplace.currency')

        if not product_id:
            raise ValidationError(_("Payment product not configured in settings."))
        if not journal_id:
            raise ValidationError(_("Payment journal not configured in settings."))

        product = self.env['product.product'].browse(int(product_id))
        journal = self.env['account.journal'].browse(int(journal_id))
        currency = int(currency_id) if currency_id else self.env.company.currency_id.id

        account = (product.property_account_expense_id
                   or product.categ_id.property_account_expense_categ_id
                   or journal.default_account_id)
        if not account:
            raise ValidationError(_(
                "Configure an expense account on the payment product or journal."))

        self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.seller_id.id,
            'ref': self.name,
            'invoice_date': self.date,
            'currency_id': currency,
            'journal_id': journal.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': self.memo,
                'account_id': account.id,
                'quantity': 1,
                'price_unit': self.payable_amount,
                'tax_ids': False,
            })],
        })
        self.seller_id.total_commission -= self.payable_amount
        self.state = 'Validated'

    @api.onchange('seller_id')
    def _onchange_seller_id(self):
        if self.seller_id:
            self.commission = self.seller_id.total_commission

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('seller.payment') or 'New'
        return super().create(vals_list)
