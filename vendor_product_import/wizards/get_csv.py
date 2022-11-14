import base64
import os
import math

import pandas as pd

from odoo import fields, models
from odoo.http import request



class WizardGetFile(models.TransientModel):
    _name = "mediod.csv.wizard"

    model_choices = [
        ('product', 'Products'),
        ('customer', 'Customer'),
        ('account', 'Chart of Accounts'),
        ('invoice', 'Invoice'),
        ('pricelist', 'Price List')]
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

        with open(file_name, "w", encoding="utf-8") as f:
            f.write(file_string)

        df = pd.read_csv(file_name, error_bad_lines=False)
        for date, row in df.T.iteritems():
            if self.model_name == 'product':
                self.import_quickbooks_product_data(row)
            elif self.model_name == 'customer':
                self.import_quickbooks_customer_data(row)
            elif self.model_name == 'account':
                self.import_chart_of_accounts(row)
            elif self.model_name == 'invoice':
                self.import_invoice(row)
            elif self.model_name == 'pricelist':

                self.import_quickbooks_listprice_data(row)


            else:
                pass

    def import_product(self, row):
        """
        Import data into products model
        :param row:
        :return:
        """
        odoo_product_dict = {"invoice_partner_display_name": str(row["Product"])}
        existing_product = request.env['mediod.product.template'].search([('name', '=', row["Name"])])
        if existing_product:
            existing_product.write(odoo_product_dict)
        else:
            request.env['product.template'].sudo().create(odoo_product_dict)

    def import_invoice(self, row):
        """
        Import data into invoices
        :param row:
        :return:
        """
        odoo_product_dict = {"invoice_partner_display_name": str(row["Customer"])}
        # odoo_product_dict_invoice["amount_total_signed"] = row["Total"]
        existing_product = request.env['mediod.product.template'].search([('name', '=', row["Number"])])
        if existing_product:
            existing_product.write(odoo_product_dict)
        else:
            request.env['account.move'].sudo().create(odoo_product_dict)

    def import_chart_of_accounts(self, row):
        """
        Import data into chart of accounts
        :param row:
        :return:
        """
        odoo_product_dict = {"name": (row["Name"]), "standard_price": row["Cost"]}
        existing_product = request.env['mediod.product.template'].search([('id', '=', row["ID"])])
        if existing_product:
            existing_product.write(odoo_product_dict)
        else:
            request.env['account.account'].sudo().create(odoo_product_dict)

    def import_quickbooks_customer_data(self, row):
        """
        Import quickbooks customer data
        :param row:
        :return:
        """
        customer_name = str(row["CustomerName"])
        customer_id = row["ï»¿CustomerListID"]
        is_active = row['CustomerIsActive']
        parent_customer = row['ParentRefFullName']
        is_existing_customer = request.env['res.partner'].search([('parent_id.name', '=', row["ParentRefFullName"])])
        customer_company = row['CompanyName']
        salutation = row['Salutation']
        customer_phone = row['Phone']
        is_company = row['CompanyName']
        if is_company:
            customer_type = "company"
        else:
            customer_type = "individual"
        contact_first_name = row['FirstName']
        contact_first_name = str(contact_first_name) if contact_first_name != 'nan' else ""

        contact_last_name = row['LastName']
        contact_last_name = str(contact_last_name) if contact_last_name != 'nan' else ""

        contact_middle_name = row['MiddleName']
        contact_middle_name = str(contact_middle_name) if contact_middle_name != 'nan' else ""

        contact_fax = row['Fax']
        contact_email = row['Email']
        contact_name = contact_first_name + " " + contact_middle_name + " " + contact_last_name
        partner_dict = {}
        try:
            is_parent = math.isnan(parent_customer)
        except:
            is_parent = False

        if is_parent:
            print(parent_customer, is_parent)
            partner_dict = {
                "name": customer_name,
                "id": customer_id,
                "active": is_active,
                "company_type": customer_type,
                "phone": customer_phone,
                "email": contact_email,
                "customer_rank": 1,
            }
        else:
            print("create contact")
            parent_customer = request.env['res.partner'].search([('name', '=', parent_customer)])
            partner_dict = {
                "name": contact_name,
                "title": salutation,
                "parent_id": parent_customer.id,
                "type": "contact",
                "email": contact_email,
                "customer_rank": 1,
                "parent": parent_customer.name,
                "fax": contact_fax,  # TODO need to add custom field fax and email data into fax rather note
                'active': is_active,
            }

        existing_parent_id = request.env['res.partner'].search([('name', '=', customer_name)])
        if partner_dict:
            if existing_parent_id:
                # existing_parent_id.write(customer_dict)
                print("existing customer")
            else:
                self.env['res.partner'].sudo().create(partner_dict)


    def import_quickbooks_product_data(self, row):
        """
        Import quickbooks product data
        :param row:
        :return:
        """
        product_dict = {}
        name = row["Name"]
        list_id = row["ï»¿ListId"]
        description_sale = row['SalesDesc']
        description_purchase=row['PurchaseDesc']
        sale_price = row['SalesPrice']
        is_active = row['IsActive']
        manufacturer_part_number = row['ManufacturerPartNumber']
        bar_code = None
        bar_code = row['BarCodeValue']
        if math.isnan(bar_code):
            # self.env['product.template'].sudo().create(bar_code = '_')
            bar_code = None
        uom_id = None
        uom_id = row['UnitOfMeasureSetRefFullName']
        if not isinstance(uom_id, str):
            if math.isnan(uom_id):
               uom_id = "Unit"
        else:
            pass
        is_existing_uom_id = request.env['product.template'].search([('name', '=', uom_id)])

        try:
            if is_existing_uom_id.id is False:
                uom_id_dict = {}
                uom_name = uom_id

                category_id = request.env['uom.category'].search([('name', '=', 'Unit')])
                category_dict = {
                    'name': category_id
                }
                if not category_id:
                    self.env['uom.uom'].sudo().create(category_dict)
                else:
                    pass
                rounding=0.0001
                uom_id_dict = {
                    "name": uom_name,
                    "category_id": category_id[0].id,
                    "rounding": rounding,
                    "uom_type":'smaller'
                }
                odoo_uom = self.env['uom.uom'].sudo().create(uom_id_dict).id
            else:
                odoo_uom = is_existing_uom_id.id
        except Exception as e:
                print(e)
        product_dict={
            "name": name,
            "list_id": list_id,
            "description_sale": description_sale,
            "description_purchase":description_purchase,
            "list_price": sale_price,
            "active": is_active,
            "manufacturer_part_number":manufacturer_part_number,
             "uom_id":odoo_uom,
            "barcode":bar_code,
        }
        is_existing_product = request.env['product.template'].search([('name', '=', row["Name"])])
        if is_existing_product:
            is_existing_product.write(product_dict)
        else:
            self.env['product.template'].sudo().create(product_dict)

    def import_quickbooks_listprice_data(self, row):
        """
        Import quickbooks pricelist data
        :param row:
        :return:
        """
        # product_dict={
        #     "name":"England",
        #     'product_item_ids':{
        #
        #     }
        # }
        #
        # self.env['product.pricelist'].sudo().create(product_dict)
        percent_price = row["Name"]
        ItemRefFullName = row['ItemRefFullName']
        product_dict = {
                "name": "Mediod",
                'item_ids': [((0, 0, {
                    "name": 'Waqas',
                    "min_quantity":1,
                    "price":1,
                    }))]
            }
        existing_parent_id = request.env['product.pricelist'].search([('name', '=', "Mediod")])
        if existing_parent_id.id is False:
                self.env['product.pricelist'].sudo().create(product_dict)
        else:
                self.env['product.pricelist'].sudo().write(product_dict)
