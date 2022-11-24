from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    ein = fields.Char('EIN')
    groupdesc = fields.Char('GroupDesc')
    groupquantity = fields.Char('GroupQuantity')
    serialnumber = fields.Char('SerialNumber')
    lotnumber = fields.Char('LotNumber')
    servicedate = fields.Char('ServiceDate')


