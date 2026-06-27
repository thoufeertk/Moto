# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
# License LGPL-3.0

from ast import literal_eval
from odoo import fields, models, _
from odoo.tools.misc import ustr
from odoo.addons.auth_signup.models.res_partner import SignupError, now


class ResUsers(models.Model):
    """Extends res.users for seller signup via website"""
    _inherit = 'res.users'

    profile_url = fields.Integer(string='Shop Url', help='Shop URL identifier')

    def _create_user_from_template(self, values):
        """Create a seller or portal user from template based on profile_url"""
        if values.get('profile_url', 0) != 0:
            template_user_id = self.env.ref(
                'motoreign_marketplace.template_seller_user').id
        else:
            template_user_id = literal_eval(
                self.env['ir.config_parameter'].sudo().get_param(
                    'base.template_portal_user_id', 'False'))
        template_user = self.browse(template_user_id)
        if not template_user.exists():
            raise ValueError(_('Signup: invalid template user'))
        if not values.get('login'):
            raise ValueError(_('Signup: no login given for new user'))
        if not values.get('partner_id') and not values.get('name'):
            raise ValueError(_('Signup: no name or partner given for new user'))
        values['active'] = True
        try:
            with self.env.cr.savepoint():
                return template_user.with_context(no_reset_password=True).copy(values)
        except Exception as e:
            raise SignupError(ustr(e))
