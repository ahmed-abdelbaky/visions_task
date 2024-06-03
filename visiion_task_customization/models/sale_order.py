from odoo import fields, models, api


class saleOrder(models.Model):
    _inherit = 'sale.order'
    tax_boolean = fields.Boolean(copy=False)

    product_lost_ids = fields.One2many('product.lost', 'sale_order_id', 'Product Lost')
    product_untax_amount = fields.Float('Untax Amount', compute='_compute_untax_product', store=True)
    product_tax_amount = fields.Float('Tax Amount')
    product_total = fields.Float('Total')

    @api.depends('product_lost_ids')
    def _compute_untax_product(self):
        for record in self.product_lost_ids:
            if record.tax_id:
                self.product_untax_amount = sum(self.product_lost_ids.mapped('price_subtotal'))
                self.product_tax_amount = (self.product_untax_amount * record.tax_id.amount) / 100
                self.product_total = self.product_untax_amount + self.product_tax_amount
                self.tax_boolean = True
            else:
                self.product_total = sum(self.product_lost_ids.mapped('price_subtotal'))
                self.tax_boolean = False

    def action_confirm(self):
        res = super().action_confirm()
        val_list = []
        for record in self.product_lost_ids:
            vals = {
                'product_id': record.product_id.id,
                'quantity': record.product_uom_qty,
                'price_unit': record.price_unit,
                'tax_ids': record.tax_id.ids,
                'price_subtotal': record.price_subtotal,

            }
            val_list.append((0, 0, vals))
        move = self.env['account.move'].create({
            'partner_id': self.partner_id.id,
            'invoice_date': fields.Datetime.today(),
            'sale_order_id': self.id,
            'invoice_line_ids': val_list,
            'move_type': 'out_invoice'
        })

        return res

    def _get_invoiced(self):
        res = super()._get_invoiced()
        if self.product_lost_ids:
            move = self.env['account.move'].search([('sale_order_id', '=', self.id)])
            self.invoice_ids = move
            self.invoice_count = len(move)
        return res
