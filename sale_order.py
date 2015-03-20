from openerp.osv import osv, fields

class sale_order(osv.osv):
    _inherit = "sale.order"

    def _get_prod_acc(self, product_id, journal_obj, context=False):
        if product_id and product_id.property_account_income:
            return product_id.property_account_income.id
        elif product_id and product_id.categ_id.property_account_income_categ:
             return product_id.categ_id.property_account_income_categ.id
        else:
            if journal_obj.default_credit_account_id:
                return journal_obj.default_credit_account_id.id
        return False
    
    def create_sales_receipt(self, cr, uid, ids, context={}):
        sale_obj = self.browse(cr, uid, ids[0], context=context)
        vals = {}
        cr_ids_list = []
        cr_ids = {}
        journal_ids = self.pool.get('account.journal').search(cr, uid, [('type', '=', 'sale')])
        if journal_ids:
            vals['journal_id'] = journal_ids[0]
            journal_obj = self.pool.get('account.journal').browse(cr, uid, journal_ids[0])
            if sale_obj and sale_obj.order_line:
                for sale_line in sale_obj.order_line:
                    cr_ids['account_id'] = self._get_prod_acc(sale_line.product_id and sale_line.product_id, journal_obj)#journal_obj.default_debit_account_id.id #Change this account to product's income account
                    cr_ids['amount'] = sale_line.price_subtotal
                    cr_ids['partner_id'] = sale_obj.partner_id.id
                    cr_ids['name'] = sale_line.name
                    cr_ids_list.append(cr_ids.copy())
            if sale_obj and sale_obj.shipcharge and sale_obj.ship_method_id and sale_obj.ship_method_id.account_id:
                cr_ids['account_id'] = sale_obj.ship_method_id.account_id.id
                cr_ids['amount'] = sale_obj.shipcharge
                cr_ids['partner_id'] = sale_obj.partner_id.id
                cr_ids['name'] = 'Shipping Charge for %s' % sale_line.name
                cr_ids_list.append(cr_ids.copy())

        else:
            vals['journal_id'] = False
        vals['partner_id'] = sale_obj.partner_id.id
        #vals['date'] = sale_obj.date_order
        vals['rel_sale_order_id'] = ids[0]
        vals['name'] = 'Auto generated Sales Receipt'
        vals['type'] = 'sale'
        vals['currency_id'] = journal_obj.company_id.currency_id.id
        vals['line_cr_ids'] = [(0, 0, cr_ids) for cr_ids in cr_ids_list]
#        vals['narration'] = voucher_obj.narration
        vals['pay_now'] = 'pay_now'
        vals['account_id'] = journal_obj.default_debit_account_id.id  
#        vals['reference'] = voucher_obj.reference
#        vals['tax_id'] = voucher_obj.tax_id.id
        vals['amount'] = sale_obj.amount_total
        vals['company_id'] = journal_obj.company_id.id
        vals['origin'] = sale_obj.name

        voucher_id = self.pool.get('account.voucher').create(cr, uid, vals, context)

        return voucher_id

    def action_wait(self, cr, uid, ids, context=None):
        ret = super(sale_order, self).action_wait(cr, uid, ids, context=context)
        for o in self.browse(cr, uid, ids, context=context):
            if (o.order_policy == 'credit_card'):
                #self.create_sales_receipt(cr, uid, [o.id])
                invoice_id = self.action_invoice_create(cr, uid, [o.id], context=context)
                wf_service = netsvc.LocalService('workflow')
                wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
                self.pool.get('account.invoice').write(cr, uid, invoice_id, {'credit_card': True}, context=context)
        return ret
    
    def action_cancel(self, cr, uid, ids, context=None):
        for sale in self.browse(cr, uid, ids, context=context):
            for picking in sale.picking_ids:
                if sale.order_policy == 'credit_card' and picking.state not in ('done', 'cancel'):
                    self.pool.get('stock.picking').action_cancel(cr, uid, [picking.id], {})
            for inv in sale.invoice_ids:
                if sale.order_policy == 'credit_card':
                    self.pool.get('account.invoice').action_cancel(cr, uid, [inv.id], {})
        return super(sale_order, self).action_cancel(cr, uid, ids, context)
    
sale_order()
