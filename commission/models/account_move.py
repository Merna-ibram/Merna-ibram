from odoo import _, api, fields, models
from datetime import date
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    agent_id = fields.Many2one(
        'res.partner',
        string='Agent',
        compute='_compute_agent_id',
        store=True
    )
    target = fields.Integer()
    target_amount = fields.Integer()
    commission_total = fields.Float(string="Commissions", readonly=True)

    @api.depends('partner_id', 'partner_id.agent_ids')
    def _compute_agent_id(self):
        for move in self:
            move.agent_id = move.partner_id.agent_ids[:1].id if move.partner_id.agent_ids else False

    def action_post(self):
        return super(AccountMove, self).action_post()

    def _compute_commission(self):
        self.ensure_one()

        # يجب أن تكون الفاتورة مدفوعة بالكامل فعليًا
        if not self.agent_id or self.payment_state != 'paid' or self.amount_residual > 0:
            return

        # جلب الدفعات المرتبطة
        payments = self.env['account.payment'].search([
            ('reconciled_invoice_ids', 'in', self.id),
            ('state', '=', 'posted')
        ])
        if not payments:
            return

        total_paid = sum(payments.mapped('amount'))
        payment_date = max(payments.mapped('date'))

        salary = getattr(self.agent_id, 'salary', 0)
        salary_threshold = salary * 2 if salary else 0
        commission_base = self.amount_untaxed_signed
        commission_amount = 0.0

        if total_paid >= salary_threshold:
            commission_amount = commission_base * 0.05

        self.commission_total = commission_amount

        # أنشئ السجل مرة واحدة فقط
        if not self.env['commission.agent.history'].search([('invoice_no', '=', self.name)], limit=1):
            self.env['commission.agent.history'].create({
                'name': self.agent_id.name,
                'agent_id': self.agent_id.id,
                'commission_id': getattr(self.agent_id, 'commission_id', False)
                    and self.agent_id.commission_id.id or False,
                'invoice_no': self.name,
                'customer_name': self.partner_id.name,
                'pad': total_paid,
                'amount_due': self.amount_residual_signed,
                'total': self.amount_untaxed_signed,
                'commission_amount': commission_amount,
                'target': self.target,
                'target_amount': self.target_amount,
                'target_percentage': (self.amount_untaxed_signed / self.target_amount * 100)
                    if self.target_amount else 0,
                'status': self.payment_state,
                'invoice_date': self.invoice_date,
                'payment_date': payment_date,
            })


class CommissionAgentHistory(models.Model):
    _name = 'commission.agent.history'
    _description = 'Commission Agent History'

    name = fields.Char(string="Name", required=True)
    agent_id = fields.Many2one('res.partner', string='Agent')
    commission_id = fields.Many2one('commission', string="Commission Type")
    invoice_no = fields.Char(string="Invoice No", required=True)
    customer_name = fields.Char(string='Customer Name')
    pad = fields.Float(string="Paid")
    amount_due = fields.Float(string="Amount Due")
    total = fields.Float(string="Total")
    commission_amount = fields.Float(string="Commission Amount")
    target_amount = fields.Float(string="Target Amount")
    target_percentage = fields.Float(string="Target Percentage")
    count_invoice = fields.Integer(string="Invoice Count")
    target = fields.Float(string="Target")
    status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
        ('pending', 'Pending'),
    ], string="Status", default='pending')
    invoice_date = fields.Date('Invoice Date')
    payment_date = fields.Date('Payment Date')


class AgentTarget(models.Model):
    _name = 'agent.target'
    _description = 'Agent Target'

    name = fields.Many2one('res.partner', string='Agent', domain=[('agent', '=', True)])
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    target_invoice = fields.Integer('Target Invoice')
    target_amount = fields.Float('Target Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approved'),
        ('done', 'Done')
    ], default='draft')

    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        today = date.today()
        first_day = today.replace(day=1)
        for rec in self:
            if rec.date_from < first_day:
                raise ValidationError('The start date cannot be earlier than the first day of the current month.')
            if rec.date_from > rec.date_to:
                raise ValidationError('The start date must be before the end date.')

    def action_send(self):
        self.write({'state': 'approve'})


# class AccountPayment(models.Model):
#     _inherit = 'account.payment'
#
#     def action_post(self):
#         res = super().action_post()
#         for payment in self:
#             invoices = payment.reconciled_invoice_ids.filtered(lambda i: i.move_type == 'out_invoice')
#             for inv in invoices:
#                 inv.refresh()
#                 # تحقق أن المبلغ المتبقي صفر فعلياً قبل الحساب
#                 if inv.payment_state == 'paid' and inv.amount_residual == 0:
#                     inv._compute_commission()
#         return res

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        res = super().action_post()
        for payment in self:
            # نتحقق أن الدفعة تمت مصالحَتها فعلاً
            invoices = payment.reconciled_invoice_ids.filtered(lambda i: i.move_type == 'out_invoice')
            for inv in invoices:
                inv.refresh()
                if inv.payment_state == 'paid' and inv.amount_residual == 0:
                    inv._compute_commission()
        return res



