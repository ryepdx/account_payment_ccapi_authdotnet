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
from openerp import netsvc

class account_voucher(osv.osv):
    '''
        Add function to hook methods authorize and cc_refund which is added on account_payment_creditcard module
    '''
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

    def check_transaction(self, cr, uid, ids, context=None):
        transaction_record = self.browse( cr, uid, ids,context)
        for record in transaction_record:
             if record.cc_p_authorize and record.cc_auth_code:
                 raise osv.except_osv(_('Error'), _("Already Authorized!"))
             if record.cc_charge and not record.cc_auth_code:
                 raise osv.except_osv(_('Error'), _("Pre-Authorize the transaction first!"))
        return True

    def authorize(self, cr, uid, ids, context=None):
        self.check_transaction(cr, uid, ids, context)
        res = self.pool.get('auth.net.cc.api').do_this_transaction(cr, uid, ids, refund=False, context=context)
        if res:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(uid, 'account.voucher', ids[0], 'proforma_voucher', cr)
        return True

    def cc_refund(self, cr, uid, ids, context=None):
        return self.pool.get('auth.net.cc.api').do_this_transaction(cr, uid, ids, refund=True, context=context)

account_voucher()