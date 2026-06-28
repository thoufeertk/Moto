# -*- coding: utf-8 -*-
from . import controller
from . import models
from . import wizard


def pre_init_hook(env):
    """Hide stock root menu from seller group on install — Odoo 19 env signature"""
    res = env.ref('stock.menu_stock_root', raise_if_not_found=False)
    res1 = env.ref('stock.group_stock_user', raise_if_not_found=False)
    if res and res1:
        res.write({'group_ids': [(3, res1.id, 0)]})
