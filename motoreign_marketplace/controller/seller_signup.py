# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19
import logging
import werkzeug
from werkzeug.urls import url_encode
from odoo import http, _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.addons.auth_signup.controllers.main import (
    AuthSignupHome, ensure_db, LOGIN_SUCCESSFUL_PARAMS, SIGN_UP_REQUEST_PARAMS,
)

_logger = logging.getLogger(__name__)
LOGIN_SUCCESSFUL_PARAMS.add('account_created')


class SellerSignup(AuthSignupHome):
    """Handles seller registration, profile pages, and shop views"""

    @http.route(['/seller/list'], type="http", auth="public", website=True)
    def seller_list(self):
        """List all published approved sellers"""
        sellers = request.env['res.partner'].sudo().search(
            [('state', '=', 'Approved'), ('is_published', '=', True)])
        return request.render(
            'motoreign_marketplace.seller_list',
            {'seller': sellers})

    def _build_seller_context(self, user_obj):
        """Shared context builder for seller profile and shop views"""
        recent_products = int(request.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.recent_products') or 5)
        review_count = int(request.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.seller_review_count') or 5)
        review = request.env['seller.review'].sudo().search(
            [('seller_id', '=', user_obj.id), ('state', '=', 'published')],
            limit=review_count)
        product = request.env['product.template'].sudo().search(
            [('seller_id', '=', user_obj.id), ('is_published', '=', True)])
        recently_added = request.env['product.template'].sudo().search(
            [('seller_id', '=', user_obj.id), ('is_published', '=', True)],
            limit=recent_products, order='id desc')
        params = request.env['res.config.settings'].sudo().get_values()
        avg = user_obj.avg_rating
        total = request.env['seller.review'].sudo().search_count(
            [('seller_id', '=', user_obj.id)])
        pct = {}
        for star in range(1, 6):
            cnt = request.env['seller.review'].sudo().search_count(
                [('seller_id', '=', user_obj.id), ('rating', '=', str(star))])
            pct[star] = round(cnt / total * 100) if total else 0
        return {
            'res_users': user_obj,
            'product': product,
            'recently_add_product': recently_added,
            'config': params,
            'cr_user': request.env.user.sudo(),
            'avg': round(avg, 2),
            'prod_count': len(product),
            'sale_count': request.env['sale.order.line'].sudo().search_count(
                [('seller_id', '=', user_obj.id)]),
            'average': avg,
            'five': str(pct[5]), 'four': str(pct[4]),
            'three': str(pct[3]), 'two': str(pct[2]), 'one': str(pct[1]),
            'review': review,
        }

    @http.route(['/seller/profile/<string:profile_url>'], type="http",
                auth="public", website=True)
    def seller_profile(self, profile_url, **kwargs):
        """Render seller profile page by profile URL slug"""
        user_obj = request.env['res.partner'].sudo().search(
            [('profile_url_value', '=', profile_url)], limit=1)
        if not user_obj:
            return request.not_found()
        ctx = self._build_seller_context(user_obj)
        return request.render('motoreign_marketplace.seller_product', ctx)

    @http.route(['/seller_shop'], type="http", auth="public",
                website=True, csrf=False)
    def seller_shop(self, seller_id=None, product_id=None, **kwargs):
        """Render seller shop by seller_id or product_id"""
        if product_id:
            pr = request.env['product.product'].sudo().browse(int(product_id))
            user_obj = pr.seller_id
        else:
            user_obj = request.env['res.partner'].sudo().browse(int(seller_id))
        ctx = self._build_seller_context(user_obj)
        return request.render('motoreign_marketplace.seller_product', ctx)

    @http.route(['/sell'], type="http", auth="public", website=True)
    def home_page(self, **post):
        """Marketplace landing / sell page"""
        params = request.env['res.config.settings'].sudo().get_values()
        bcome_seller = request.env['ir.config_parameter'].sudo().get_param(
            'motoreign_marketplace.bcome_seller')
        params['bcome_seller'] = bcome_seller in ['True', '1', True]
        is_seller = request.env.user.has_group(
            'motoreign_marketplace.motoreign_marketplace_seller')
        return request.render('motoreign_marketplace.sell_page', {
            'config': params,
            'is_seller': is_seller,
        })

    @http.route('/seller_reg', type='http', auth='public', website=True,
                sitemap=False, csrf=False)
    def seller_signup(self, *args, **kw):
        """Seller registration form (extends auth_signup)"""
        qcontext = self.get_auth_signup_qcontext()
        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()
        if 'error' not in qcontext and request.httprequest.method == 'POST':
            if request.env["res.partner"].sudo().search(
                    [("profile_url_value", "=", kw.get("profile_url"))]):
                qcontext["error"] = _(
                    "Another user has already registered with this profile URL.")
            else:
                try:
                    qcontext['profile_url'] = 1
                    self.do_signup(qcontext)
                    base_url = request.env['ir.config_parameter'].sudo().get_param(
                        'web.base.url')
                    request.env["res.partner"].sudo().search(
                        [("email", "=", kw.get("login"))]).write({
                            'profile_url': base_url + "/seller/profile/" + kw.get('profile_url'),
                            'profile_url_value': kw.get('profile_url'),
                        })
                    if qcontext.get('token'):
                        user = request.env['res.users']
                        user_sudo = user.sudo().search(
                            user._get_login_domain(qcontext.get('login')),
                            order=user._get_login_order(), limit=1)
                        tmpl = request.env.ref(
                            'auth_signup.mail_template_user_input_invite',
                            raise_if_not_found=False)
                        if user_sudo and tmpl:
                            tmpl.sudo().send_mail(user_sudo.id, force_send=True)
                    request.session.logout(keep_db=True)
                    request.session.authenticate(
                        request.session.db, kw.get('login'), kw.get('password'))
                    return request.redirect('/web')
                except UserError as e:
                    qcontext['error'] = e.args[0]
                except (SignupError, AssertionError) as e:
                    if request.env["res.users"].sudo().search(
                            [("login", "=", qcontext.get("login"))]):
                        qcontext["error"] = _(
                            "Another user is already registered with this email.")
                    else:
                        _logger.error("%s", e)
                        qcontext['error'] = _("Could not create a new account.")
        elif 'signup_email' in qcontext:
            user = request.env['res.users'].sudo().search([
                ('email', '=', qcontext.get('signup_email')),
                ('state', '!=', 'new'),
            ], limit=1)
            if user:
                return request.redirect('/web/login?%s' % url_encode(
                    {'login': user.login, 'redirect': '/web'}))
        return request.render('motoreign_marketplace.mark', qcontext)

    def _prepare_signup_values(self, qcontext):
        """Prepare signup values including seller profile_url"""
        values = {k: qcontext.get(k) for k in ('login', 'name', 'password')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '')
        if lang in supported:
            values['lang'] = lang
        values['profile_url'] = int(qcontext.get('profile_url')) if qcontext.get('profile_url') else 0
        return values
