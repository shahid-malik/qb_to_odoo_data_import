import base64
import math
import os
import re

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
        i =0
        for date, row in df.T.items():
            print("#####################################################################################")
            print(i)
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
            i = i+1

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

    def check_is_nan(self, val):
        try:
            math.isnan(val)
            return True
        except:
            return False

    def import_quickbooks_customer_data(self, row):
        """
        Import quickbooks customer data
        :param row:
        :return:
        """
        customer_name = str(row["CustomerName"])
        customer_list_id = row["ï»¿CustomerListID"]
        is_active = row['CustomerIsActive']
        parent_name = row['ParentRefFullName']
        company_name = row['CompanyName']
        phone = row['Phone'] if self.check_is_nan(row['Phone']) is False else None
        email = row['Email'] if self.check_is_nan(row['Email']) is False else None
        fax = row['Fax'] if self.check_is_nan(row['Fax']) is False else None
        notes = row['Notes'] if self.check_is_nan(row['Notes']) is False else None
        street = row['BillAddr3'] if self.check_is_nan(row['BillAddr3']) is False else None
        city = row['BillCity'] if self.check_is_nan(row['BillCity']) is False else None
        zip = row['BillPostalCode'] if self.check_is_nan(row['BillPostalCode']) is False else None
        state_code = row['BillState'] if self.check_is_nan(row['BillState']) is False else ''
        state_id = self.env['res.country.state'].sudo().search([('code', '=', state_code)])
        if company_name:
            company_type = "company"
        else:
            company_type = "person"

        try:
            # will return False if Parent name is Present
            is_parent = math.isnan(parent_name)
        except:
            is_parent = False

        if is_parent:
            partner_dict = {
                'name': customer_name,
                'customer_list_id': customer_list_id,
                'company_type': company_type,
                'street': street,
                'city': city,
                'state_id': state_id[0].id if state_id else None,
                'zip': zip,
                'customer_rank': 1,
                'phone': phone,
                'email': email,
                'fax': fax,
                'comment': notes,
                'active': is_active,
            }
        else:
            parent_id = self.env['res.partner'].sudo().search([('name', '=', parent_name)])
            partner_dict = {
                'name': customer_name,
                'parent_id': parent_id[0].id if parent_id else None,
                'customer_list_id': customer_list_id,
                'company_type': company_type,
                'street': street,
                'city': city,
                'state_id': state_id[0].id if state_id else None,
                'zip': zip,
                'customer_rank': 1,
                'phone': phone,
                'email': email,
                'fax': fax,
                'comment': notes,
                'active': is_active,
            }

        existing_customer = self.env['res.partner'].sudo().search([('name', '=', customer_name)])
        if existing_customer:
            existing_customer[0].write(partner_dict)
        else:
            self.env['res.partner'].sudo().create(partner_dict)

        # customer_name = str(row["CustomerName"])
        # customer_list_id = row["ï»¿CustomerListID"]
        # is_active = row['CustomerIsActive']
        # parent_customer = row['ParentRefFullName']
        # is_existing_customer = request.env['res.partner'].search([('parent_id.name', '=', row["ParentRefFullName"])])
        # # customer_company = row['CompanyName']
        # salutation = row['Salutation']
        # customer_phone = row['Phone']
        # is_company = row['CompanyName']
        # if is_company:
        #     customer_type = "company"
        # else:
        #     customer_type = "person"
        # contact_first_name = row['FirstName']
        # contact_first_name = str(contact_first_name) if type(contact_first_name) != float else ""
        #
        # contact_last_name = row['LastName']
        # contact_last_name = str(contact_last_name) if type(contact_last_name) != float else ""
        #
        # contact_middle_name = row['MiddleName']
        # contact_middle_name = str(contact_middle_name) if type(contact_middle_name) != float else ""
        #
        # contact_fax = row['Fax']
        # contact_email = row['Email']
        # contact_name = contact_first_name + " " + contact_middle_name + " " + contact_last_name
        # partner_dict = {}
        # try:
        #     is_parent = math.isnan(parent_customer)
        # except:
        #     is_parent = False
        #
        # #  without parent_id
        # if is_parent:
        #     print(parent_customer, is_parent)
        #     partner_dict = {
        #         "name": customer_name,
        #         "customer_list_id": customer_list_id,
        #         "fax": contact_fax,
        #         "active": is_active,
        #         "company_type": customer_type,
        #         # "phone": customer_phone,
        #         # "email": contact_email,
        #         # "customer_rank": 1
        #     }
        # # with parent id
        # else:
        #     print("create contact")
        #     parent_customer = request.env['res.partner'].search([('name', '=', parent_customer)])
        #     partner_dict = {
        #         "name": contact_name,
        #         # "title": salutation,
        #         "parent_id": parent_customer[0].id if parent_customer else None,
        #         # "type": "contact",
        #         # "email": contact_email,
        #         # "customer_rank": 1,
        #         # "parent": parent_customer[0].name if parent_customer else None,
        #         'customer_list_id': customer_list_id,
        #         "company_type": customer_type,
        #         "fax": contact_fax,  # TODO need to add custom field fax and email data into fax rather note
        #         'active': is_active,
        #     }
        #
        # existing_customer = request.env['res.partner'].search([('name', '=', contact_name)])
        # if partner_dict:
        #     if existing_customer:
        #         existing_customer[0].write(partner_dict)
        #     else:
        #         self.env['res.partner'].sudo().create(partner_dict)
        # else:
        #     pass

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
        description_purchase = row['PurchaseDesc']
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
                rounding = 0.0001
                uom_id_dict = {
                    "name": uom_name,
                    "category_id": category_id[0].id,
                    "rounding": rounding,
                    "uom_type": 'smaller'
                }
                odoo_uom = self.env['uom.uom'].sudo().create(uom_id_dict).id
            else:
                odoo_uom = is_existing_uom_id.id
        except Exception as e:
            print(e)
        product_dict = {
            "name": name,
            "list_id": list_id,
            "description_sale": description_sale,
            "description_purchase": description_purchase,
            "list_price": sale_price,
            "active": is_active,
            "manufacturer_part_number": manufacturer_part_number,
            "uom_id": odoo_uom,
            "barcode": bar_code,
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
        # ///////////////////////////////////////////


        pricelist_id = request.env['product.pricelist'].search([('name', '=', "P9")], limit=1,
                                                                        order='id desc')
        if not pricelist_id:
            pricelist_id = self.env['product.pricelist'].create({'name': 'P9'})
        else:
            product_list = {}
            list_id = row['ListID']
            item_name = row['ItemRefFullName']
            discount_price = row["CustomPrice"]
            standard_test_price = row["Name"]
            a = re.findall(r"[-+]?\d*\.\d+|\d+", standard_test_price)
            standard_price = float(a[0])
            product_list = {
                    "list_id": list_id,
                    "name": item_name,
                    "list_price": discount_price,
                    "standard_price":standard_price,
                }
            self.env['product.template'].sudo().create(product_list)
            a = re.findall(r"[-+]?\d*\.\d+|\d+", standard_test_price)
            item_price = float(a[0])
            compute_price = 'percentage'
            applied_on = '1_product'
            product_tmpl_id = request.env['product.template'].search([('name', '=', item_name)])
            print(product_tmpl_id)
            if product_tmpl_id:
               pricelist_id.item_ids = [(0, 0,{"pricelist_id": pricelist_id.id,
                                                         "percent_price": item_price,
                                                         "name": item_name,
                                                         "compute_price": compute_price,
                                                         "applied_on": applied_on,
                                                         "product_tmpl_id": product_tmpl_id[0].id if product_tmpl_id else None})]

        return True
 # res = [int(i) for i in row["Name"] if i.isdigit()]
            # item_price = str(res)
            # s = str(res[0])
            # v = str(res[1])
            # item_price = s + v
            # item_price = float(row["Name"].split('%')[0])
# else: