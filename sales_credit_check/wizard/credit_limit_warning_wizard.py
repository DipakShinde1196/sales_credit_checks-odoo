from odoo import models, fields


class CreditLimitWarningWizard(models.TransientModel):
    _name = 'credit.limit.warning.wizard'
    _description = 'Credit Limit Warning Wizard'

    sale_order_id = fields.Many2one('sale.order', required=True)
    partner_id = fields.Many2one('res.partner', required=True)

    def action_yes(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'res_id': self.partner_id.id,
            'target': 'current',
        }

    def action_no(self):
        return {'type': 'ir.actions.act_window_close'}
