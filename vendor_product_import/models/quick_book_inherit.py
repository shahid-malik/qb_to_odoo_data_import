from odoo import models, fields,api


class ResPartner(models.Model):
    _inherit = "res.partner"

    customer_list_id = fields.Char('Customer List Id')
    parent = fields.Char('Parent')