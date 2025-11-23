from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        domain=[('move_type', 'in', ['out_invoice', 'in_invoice'])],
        compute='_compute_invoice_id',
        store=True,
        readonly=False,
    )

    price_before_tax = fields.Float(
        string='Price Before Tax',
        compute='_compute_price_before_tax',
        store=True,
        readonly=True,
    )

    @api.depends('reconciled_invoice_ids', 'reconciled_bill_ids')
    def _compute_invoice_id(self):
        for rec in self:
            # جمع فواتير العملاء والموردين
            all_invoices = rec.reconciled_invoice_ids | rec.reconciled_bill_ids
            # يربط الفاتورة إذا فيه فاتورة واحدة فقط
            rec.invoice_id = all_invoices[0] if len(all_invoices) == 1 else False

    @api.depends('invoice_id', 'amount', 'invoice_id.amount_untaxed', 'invoice_id.amount_total')
    def _compute_price_before_tax(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.amount_total:
                # حساب نسبة المبلغ المدفوع من إجمالي الفاتورة
                payment_ratio = rec.amount / rec.invoice_id.amount_total
                # تطبيق النسبة على المبلغ قبل الضريبة
                rec.price_before_tax = rec.invoice_id.amount_untaxed * payment_ratio
            else:
                rec.price_before_tax = 0.0