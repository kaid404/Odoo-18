from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_button_noumi = fields.Boolean('NOUMI Sales', default=False)


    def action_sale_order_print(self):
        print("hyyyyyyyyyyyyyyyyyyyyyyyyyy")
        return self.env.ref('fincera_sales_qutation_report.action_report_saleorder_fincera').report_action(self)




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    show_button_noumi = fields.Boolean('NOUMI Sales', default=False)



    def action_account_payment_print(self):
        date = {'id':self.id}
        print("hyyyyyyyyyyyyyyyyyyyyyyyyyy")
        return self.env.ref('account.action_report_payment_receipt').report_action(self)






