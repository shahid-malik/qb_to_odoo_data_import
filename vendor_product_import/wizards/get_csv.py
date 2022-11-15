import base64
import math
import os

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
        customer_list_id = row["ï»¿CustomerListID"] if "ï»¿CustomerListID" in row else row["CustomerListID"]
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
        salutation = row['Salutation'] if self.check_is_nan(row['Salutation']) is False else None
        if salutation is not None:
            partner_title = self.env['res.partner.title'].sudo().search([('name', '=', salutation)])
            if partner_title:
                customer_title = partner_title[0].id
            else:
                customer_title = self.env['res.partner.title'].sudo().create({'name': salutation}).id
        else:
            customer_title = None

        firstname = row['FirstName'] if self.check_is_nan(row['FirstName']) is False else None
        middle_name = row['MiddleName'] if self.check_is_nan(row['MiddleName']) is False else None
        lastname = row['LastName'] if self.check_is_nan(row['LastName']) is False else None

        payment_term_name = row['TermsRefFullName'] if self.check_is_nan(row['TermsRefFullName']) is False else None
        if payment_term_name is not None:
            payment_term_id = self.env['account.payment.term'].sudo().search([('name', '=', payment_term_name)])
            if payment_term_id:
                payment_term = payment_term_id[0].id
            else:
                payment_term = self.env['account.payment.term'].sudo().create({
                    'name': payment_term_name,
                    'note': 'Payment_term:' + str(payment_term_name),
                    'active': True,
                    'sequence': 10,
                }).id
        else:
            payment_term = None

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
                'customer_rank': 1,
                'title': customer_title,
                'property_payment_term_id': payment_term,
                'first_name': firstname,
                'middle_name': middle_name,
                'last_name': lastname,
                'street': street,
                'city': city,
                'state_id': state_id[0].id if state_id else None,
                'zip': zip,
                'type': 'contact',
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
                'customer_rank': 1,
                'title': customer_title,
                'property_payment_term_id': payment_term,
                'first_name': firstname,
                'middle_name': middle_name,
                'last_name': lastname,
                'street': street,
                'city': city,
                'state_id': state_id[0].id if state_id else None,
                'zip': zip,
                'type': 'invoice',
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
            new_rec = self.env['res.partner'].sudo().create(partner_dict)

        # shipping Address of type Delivery
        ship_addr_1 = row['ShipAddr1'] if self.check_is_nan(row['ShipAddr1']) is False else None
        ship_addr_2 = row['ShipAddr2'] if self.check_is_nan(row['ShipAddr2']) is False else None
        ship_addr_3 = row['ShipAddr3'] if self.check_is_nan(row['ShipAddr3']) is False else None
        ship_city = row['ShipCity'] if self.check_is_nan(row['ShipCity']) is False else None
        ship_state_code = row['ShipState'] if self.check_is_nan(row['ShipState']) is False else None
        ship_state_id = self.env['res.country.state'].sudo().search([('code', '=', ship_state_code)])
        ship_country_code = row['ShipCountry'] if self.check_is_nan(row['ShipCountry']) is False else None
        ship_country_id = self.env['res.country'].sudo().search([('code', '=', ship_country_code)])
        ship_postal_code = row['ShipPostalCode'] if self.check_is_nan(row['ShipPostalCode']) is False else None
        ship_note = row['ShipNote'] if self.check_is_nan(row['ShipNote']) is False else None

        shipping_address_dict = {
            'type': 'delivery',
            'name': ship_addr_1,
            'street': ship_addr_2,
            'street2': ship_addr_3,
            'city': ship_city,
            'state_id': ship_state_id[0].id if ship_state_id else None,
            'zip': ship_postal_code,
            'country_id': ship_country_id[0].id if ship_country_id else None,
            'comment': ship_note,
            'parent_id': existing_customer[0].id if existing_customer else new_rec.id
        }

        if ship_addr_1 is not None:
            existing_ship_address = self.env['res.partner'].sudo().search(
                ['&', '&', ('type', '=', 'delivery'), ('name', '=', ship_addr_1),
                 ('parent_id','=', existing_customer[0].id if existing_customer else None)])

            if existing_ship_address:
                existing_ship_address[0].write(shipping_address_dict)
            else:
                self.env['res.partner'].sudo().create(shipping_address_dict)
        else:
            pass

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

        existing_pricelist_id = request.env['product.pricelist'].search([('name', '=', "P3")], limit=1,
                                                                        order='id desc')
        if not existing_pricelist_id:
            pricelist_id = self.env['product.pricelist'].create({'name': 'P3'})
        else:
            pricelist_id = existing_pricelist_id
            item_price = float(row["Name"].split('%')[0])
            if not item_price:
                item_price = float(row["Name"].split('%')[0])
            item_name = row['ItemRefFullName']
            compute_price = 'percentage'
            applied_on = '1_product'
            product_tmpl_id = self.env['product.template'].search([('name', '=', 'item_name')])
            if product_tmpl_id:
                existing_pricelist_id.item_ids = [(0, 0,
                                                   {"pricelist_id": pricelist_id.id,
                                                    "percent_price": item_price,
                                                    "name": item_name,
                                                    "compute_price": compute_price, "applied_on": applied_on,
                                                    "product_tmpl_id": product_tmpl_id})]

# if not product_tmpl_id:
#     product_list = {}
#     list_id = row['ListID']
#     item_name = row['ItemRefFullName']
#     discount_price = row["Name"].split('%')[0]
#     product_list = {
#         "list_id": list_id,
#         "name": item_name,
#         "list_price": discount_price,
#     }
#     self.env['product.template'].sudo().create(product_list)
# else:
