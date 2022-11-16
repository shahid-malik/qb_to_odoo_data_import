from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_list_id = fields.Char('Customer List Id')
    parent = fields.Char('Parent')
    fax = fields.Char(string='Fax')
    first_name = fields.Char(string='First name')
    middle_name = fields.Char(string='Middle name')
    last_name = fields.Char(string='Last name')
