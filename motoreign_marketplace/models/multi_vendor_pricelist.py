# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class MultiVendorPriceList(models.Model):
    """Custom pricelist lines linked to vendor products"""
    _name = 'multi.vendor.pricelist'
    _description = "Multi Vendor Pricelist"

    price_list_id = fields.Many2one('product.pricelist', string='Pricelist', help='Pricelist')
    price_of_pricelist = fields.Float(required=True, string='Price', help='Price')
    min_qty = fields.Integer(required=True, string='Minimum Quantity', help='Minimum quantity')
    start_date = fields.Date(required=True, string='Start Date', help='Start Date')
    end_date = fields.Date(required=True, string='End Date', help='End Date')
    product_inv_id = fields.Many2one('product.template', string='Product',
                                     help='Product', ondelete='cascade')

    @api.ondelete(at_uninstall=False)
    def _delete_pricelist_item(self):
        """Remove linked product.pricelist.item rows when this line is deleted"""
        for rec in self:
            if rec.id:
                self.env.cr.execute(
                    "DELETE FROM product_pricelist_item WHERE pricelist_multivendor_id = %s",
                    (rec.id,)
                )
