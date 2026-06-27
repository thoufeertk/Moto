# -*- coding: utf-8 -*-
# Motoreign Multi Vendor Marketplace - Odoo 19 Enterprise
# Copyright (C) 2025 Motoreign (https://motoreign.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from . import controller
from . import models
from . import wizard


def pre_init_hook(env):
    """Hide inventory root menu from seller group on install"""
    res = env.ref('stock.menu_stock_root')
    res1 = env.ref('stock.group_stock_user')
    res.write({'group_ids': [(3, res1.id, 0)]})
