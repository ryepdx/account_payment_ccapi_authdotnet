# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

class account_voucher(osv.osv):
    
    _inherit = 'account.voucher'
    _columns = {
        'origin': fields.char('Origin', size=16, help='Mentions the reference of Sale/Purchase document'),
    }

    def setParameter(self, parameters={}, key=None, value=None):
        if key != None and value != None and str(key).strip() != '' and str(value).strip() != '':
            parameters[key] = str(value).strip()
        else:
            raise osv.except_osv(
                _('Error'), _('Incorrect parameters passed to setParameter(): {0}:{1}'.format(key, value)))
        return parameters

account_voucher()
