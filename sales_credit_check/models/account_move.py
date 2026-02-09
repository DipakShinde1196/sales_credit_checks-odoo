from odoo import models, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        move = super().create(vals)

        if move.move_type == 'out_invoice' and not move.invoice_origin:
            partner = move.partner_id.commercial_partner_id

            open_orders = self.env['sale.order'].search([
                ('partner_id.commercial_partner_id', '=', partner.id),
                ('state', 'in', ['sale', 'done']),
                ('order_line.invoice_status', '!=', 'invoiced')
            ], limit=1)

            if open_orders:
                raise UserError(
                    "You cannot create a manual invoice for this customer "
                    "because there are open Sales Orders that are not fully invoiced."
                )
        return move
