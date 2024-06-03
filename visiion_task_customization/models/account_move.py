from odoo import models, fields, api
from odoo.exceptions import UserError


class accountMove(models.Model):
    _inherit = 'account.move'

    sale_order_id = fields.Many2one('sale.order')

    def action_post(self):
        res = super().action_post()

        if self.sale_order_id:
            # if not self.env.user.has_group('visiion_task_customization.sales_manger_group'):
            if self.env.user.has_group('visiion_task_customization.pre_sales_group'):
                if self.amount_total > 100:
                    raise UserError('ToTal Invoice above 100')
                else:
                    return res
            if self.env.user.has_group('visiion_task_customization.sales_user_group'):
                if self.amount_total > 1000:
                    raise UserError('ToTal Invoice above 1000')
                else:
                    return res
        return res
