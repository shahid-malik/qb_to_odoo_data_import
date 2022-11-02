import base64
import os
import re

import pandas as pd
from odoo import fields, models
from odoo.http import request


class WizardGetFile(models.TransientModel):
    _name = "mediod.csv.wizard"

    model_choices =  [
                      ('product', 'Products'),
                      ('customer', 'Customer'),
                      ('account', 'Chart of Accounts'),
                      ('invoice', 'Invoice')]
    csv_file = fields.Binary('Upload CSV', required=True)
    # template_name = fields.Many2one('mediod.vendor.template', 'Template Name', required=True)
    model_name = fields.Selection(model_choices, 'Model Name')

    # On click of import button on wizard
    # and import the csv file in that model
    def import_csv(self):
        file = base64.b64decode(self.csv_file)
        file_string = file.decode('unicode_escape')
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = os.path.join(cur_dir, "demofile2.csv")
        f = open(file_name, "w")
        f.write(file_string)
        f.close()
        df = pd.read_csv(file_name, error_bad_lines=False)
        odoo_product_dict = {}
        for date, row in df.T.iteritems():
            if self.model_name == 'product':
                odoo_product_dict["name"] = str(row["Name"])
                odoo_product_dict["standard_price"] = row["Cost"]
                existing_product = request.env['mediod.product.template'].search([('name', '=', row["Name"])])
                if existing_product:
                   existing_product.write(odoo_product_dict)
                else:
                    request.env['product.template'].sudo().create(odoo_product_dict)
            elif self.model_name == 'customer':
                odoo_product_dict["name"] = str(row["CustomerName"])
                odoo_product_dict["customer_list_id"] = row["ï»¿CustomerListID"]
                odoo_product_dict["parent"] = str(row["ParentRefFullName"])
                odoo_product_dict["property_payment_term_id"] = row["TermsRefFullName"]
                odoo_product_dict["phone"] = row["Phone"]
                odoo_product_dict["active"] = row["CustomerIsActive"]
                # odoo_product_dict["company_id"] = row["Company"]
                existing_product = request.env['mediod.product.template'].search([('name', '=', row["CustomerName"])])
                if existing_product:
                   existing_product.write(odoo_product_dict)
                else:
                 request.env['res.partner'].sudo().create(odoo_product_dict)
            elif self.model_name == 'account':
                odoo_product_dict["name"] = (row["Name"])
                odoo_product_dict["standard_price"] = row["Cost"]
                existing_product = request.env['mediod.product.template'].search([('id', '=', row["ID"])])
                if existing_product:
                   existing_product.write(odoo_product_dict)
                else:
                    request.env['account.account'].sudo().create(odoo_product_dict)
            elif self.model_name == 'invoice':
                odoo_product_dict["invoice_partner_display_name"] = str(row["Customer"])
                # odoo_product_dict_invoice["amount_total_signed"] = row["Total"]
                existing_product = request.env['mediod.product.template'].search([('name', '=', row["Number"])])
                if existing_product:
                   existing_product.write(odoo_product_dict)
                else:
                     request.env['account.move'].sudo().create(odoo_product_dict)
            else:
                request.env['res.partner'].sudo().create(odoo_product_dict)
