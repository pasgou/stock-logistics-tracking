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

class stock_tracking(osv.osv):

    _inherit = 'stock.tracking'
    
    def hierarchy_ids(self, tracking):
        result_list = [tracking]
        for child in tracking.child_ids:
            result_list.extend(self.hierarchy_ids(child))
        return result_list

    def _get_child_products(self, cr, uid, ids, field_name, arg, context=None):
        packs = self.browse(cr, uid, ids)
        res = {}
        for pack in packs:
            res[pack.id] = []
            childs = self.hierarchy_ids(pack)
            for child in childs:
                for prod in child.product_ids:
                    res[pack.id].append(prod.id)
        return res

    def _get_child_serials(self, cr, uid, ids, field_name, arg, context=None):
        packs = self.browse(cr, uid, ids)
        res = {}
        for pack in packs:
            res[pack.id] = []
            childs = self.hierarchy_ids(pack)
            for child in childs:
                for serial in child.serial_ids:
                    res[pack.id].append(serial.id)
        return res
    
    _columns = { 
                
            'parent_id': fields.many2one('stock.tracking', 'Parent'),
            'child_ids': fields.one2many('stock.tracking', 'parent_id', 'Children', readonly=True),
            'ul_id': fields.many2one('product.ul', 'Logistic unit'),
            'child_product_ids': fields.function(_get_child_products, method=True, type='one2many', obj='product.stock.tracking', string='Child Products'),
            'child_serial_ids': fields.function(_get_child_serials, method=True, type='one2many', obj='serial.stock.tracking', string='Child Serials'),
            
        }
    
#    def get_products_process(self, cr, uid, pack_ids, context=None):
#        for pack in pack_ids:
#            for child in pack.child_ids:
#                pack_ids.extend(self.hierarchy_ids(child))
#        return super(stock_tracking, self).get_products_process(cr, uid, pack_ids, context=context)
#    
#    def get_serial_process(self, cr, uid, pack_ids, context=None):
#        for pack in pack_ids:
#            for child in pack.child_ids:
#                pack_ids.extend(self.hierarchy_ids(child))
#        return super(stock_tracking, self).get_serial_process(cr, uid, pack_ids, context=context)

    def get_products(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        stock_track = self.pool.get('product.stock.tracking')
        for pack in pack_ids:
            childs = self.hierarchy_ids(pack)
            for child in childs:
                product_ids = [x.id for x in child.product_ids]
                stock_track.unlink(cr, uid, product_ids)
                product_list = {}
                for x in child.current_move_ids:
                    if x.location_dest_id.id == child.location_id.id:
                        if x.product_id.id not in product_list.keys():
                            product_list.update({x.product_id.id:x.product_qty})
                        else:
                            product_list[x.product_id.id] += x.product_qty
                for product in product_list.keys():
                    stock_track.create(cr, uid, {'product_id': product, 'quantity': product_list[product], 'tracking_id': child.id})
        return True

    def get_serials(self, cr, uid, ids, context=None):
        pack_ids = self.browse(cr, uid, ids, context)
        serial_track = self.pool.get('serial.stock.tracking')
        serial_obj = self.pool.get('stock.production.lot')
        for pack in pack_ids:
            childs = self.hierarchy_ids(pack)
            for child in childs:
                serial_ids = [x.id for x in child.serial_ids]
                serial_track.unlink(cr, uid, serial_ids)
                serial_list = {}
                for x in child.current_move_ids:
                    if x.location_dest_id.id == child.location_id.id:
                        if x.prodlot_id.id not in serial_list.keys():
                            serial_list.update({x.prodlot_id.id:x.product_qty})
                        else:
                            serial_list[x.prodlot_id.id] += x.product_qty
                for serial in serial_list.keys():
                    if serial:
                        serial_track.create(cr, uid, {'serial_id': serial, 'quantity': serial_list[serial], 'tracking_id': child.id}, context=context)
                        serial_obj.write(cr, uid, [serial], {'tracking_id': child.id}, context=context)
        return True
    
    def _check_parent_id(self, cr, uid, ids, context=None):
        lines = self.browse(cr, uid, ids, context=context)

        if lines[0].parent_id:
            if lines[0].ul_id.capacity_index > lines[0].parent_id.ul_id.capacity_index:
                return False
        return True

    _constraints = [(_check_parent_id, 'Bad parent type selection. Please try again.',['parent_id'] ),]

    _defaults = {
#        'state': 'open',
        'location_id': lambda x, y, z, c: c and c.get('location_id') or False,
    }
    
stock_tracking()
    
class product_ul(osv.osv):
        _inherit = "product.ul"
        _description = "Shipping Unit"
        _columns = {
             'capacity_index': fields.integer('Capacity index'),
        }
        _order = 'capacity_index'
product_ul()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
