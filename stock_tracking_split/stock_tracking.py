 # -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from datetime import datetime
from osv import fields, osv
from tools.translate import _
import netsvc

class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    _columns = {
        'use_exist' : fields.boolean('Existing Lots', invisible=True),
     }
    _defaults = {
        'use_exist': lambda *a: True,
    }
    def default_get(self, cr, uid, fields, context=None):
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context=context)
        res.update({'use_exist': True})
        return res

split_in_production_lot()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
