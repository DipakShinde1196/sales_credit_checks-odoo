from odoo import fields, models, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    credit_warning_shown = fields.Boolean(string='Credit Show Warning', default=False)
    block_invoice = fields.Boolean(string='Block Invoice', compute='_compute_block_invoice', store=True,)
    show_credit_limit_wizard = fields.Boolean(default=False)
    show_credit_limit_button = fields.Boolean(compute="_compute_show_credit_limit_button", store=False)

    @api.depends('amount_untaxed', 'partner_id.credit_limit')
    def _compute_block_invoice(self):
        for order in self:
            if order.partner_id.credit_limit:
                order.block_invoice = order.amount_untaxed > order.partner_id.credit_limit
            else:
                order.block_invoice = True

    @api.depends('partner_id', 'partner_id.credit_limit')
    def _compute_show_credit_limit_button(self):
        for order in self:
            order.show_credit_limit_button = bool(
                order.partner_id and order.partner_id.credit_limit <= 0
            )

    @api.onchange('partner_id')
    def _onchange_partner_credit_limit(self):
        for order in self:
            if (
                    order.partner_id
                    and not order.partner_id.credit_limit
                    and not order.credit_warning_shown
            ):
                order.credit_warning_shown = True
                order.show_credit_limit_wizard = True

    def action_open_credit_limit_wizard(self):
        self.ensure_one()
        self.show_credit_limit_wizard = False

        return {
            'type': 'ir.actions.act_window',
            'name': 'Credit Limit Warning',
            'res_model': 'credit.limit.warning.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_partner_id': self.partner_id.id,
            }
        }

    def _create_invoices(self, grouped=False, final=False):
        for order in self:
            if order.block_invoice:
                raise UserError(
                    "Invoice cannot be created because the Sales Order total "
                    "exceeds the customer's credit limit."
                )
        return super()._create_invoices(grouped=grouped, final=final)
