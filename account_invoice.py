from copy import copy
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def refund(self, cr, uid, ids, **kwargs):
        context = kwargs.get("context", None)
        res = super(account_invoice, self).refund(cr, uid, ids, **kwargs)
        cc_invoice_ids = self.search(cr, uid, [('id', 'in', ids), ('credit_card', '=', True)], context=context)
        move_ids  = [i.move_id.id for i in self.browse(cr, uid, cc_invoice_ids, context=context)]
        voucher_pool = self.pool.get('account.voucher')
        voucher_pool.cc_refund(self, cr, uid, voucher_pool.search(
            cr, uid, [('move_id', 'in', move_ids)], context=context), context=context)

        return res