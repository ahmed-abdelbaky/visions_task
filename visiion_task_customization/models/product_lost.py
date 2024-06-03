from odoo import fields, models, api
from odoo.tools import float_compare


class ProductLost(models.Model):
    _name = 'product.lost'

    name = fields.Char()
    currency_id = fields.Many2one("res.currency")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    sale_order_id = fields.Many2one('sale.order')
    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        change_default=True, ondelete='restrict', check_company=True, index='btree_not_null',
        domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")

    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0,
      )

    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        check_company=True)
    price_unit = fields.Float(
        string="Unit Price",
        related='product_id.lst_price',
        digits='Product Price')
    price_subtotal = fields.Monetary(
        string="Subtotal",
        compute='_compute_amount',
        store=True, precompute=True)

    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for record in self:
            record.price_subtotal = record.product_uom_qty * record.price_unit
            # if record.tax_id:
            #     record.untax_amount += sum(self.mapped('price_subtotal'))
            #     record.tax_amount = (record.untax_amount * record.tax_id.amount)/100
            #     record.total = record.untax_amount + record.tax_amount
            # else:
            #     record.total = sum(self.mapped('price_subtotal'))
