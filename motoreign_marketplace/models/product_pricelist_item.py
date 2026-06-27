# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    """Extends pricelist item to link back to multi-vendor pricelist"""
    _inherit = 'product.pricelist.item'

    pricelist_multivendor_id = fields.Many2one(
        'multi.vendor.pricelist',
        string='Pricelist Item',
        help='Linked multi-vendor pricelist line')

    @api.ondelete(at_uninstall=False)
    def _delete_multivendor_pricelist(self):
        """Remove linked multi_vendor_pricelist row when pricelist item is deleted"""
        for rec in self:
            if rec.pricelist_multivendor_id:
                self.env.cr.execute(
                    "DELETE FROM multi_vendor_pricelist WHERE id = %s",
                    (rec.pricelist_multivendor_id.id,)
                )
