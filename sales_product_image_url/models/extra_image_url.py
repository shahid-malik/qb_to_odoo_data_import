# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api
import base64
import requests


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sh_extra_image_url = fields.Text("Extra Image Url")
    sh_mee = fields.Text("Last Sync Images")
    product_image = fields.Char('Product Image Url')

    @api.onchange('product_image')
    def onchange_image(self):
        link = self.product_image
        if link:
            if "http://" in link or "https://" in link:
                photo = base64.b64encode(requests.get(link).content)
                val = {
                    'image_1920': photo,
                }
                return {'value': val}

    def get_image_urls(self):
        bad_link = []
        self.sh_mee = ''
        message = ''
        if self.sh_extra_image_url:
            if self.product_template_image_ids:
                self.product_template_image_ids.unlink()
            list_url = self.sh_extra_image_url.split(",")
            for urls in list_url:
                link = urls
                if "http://" in link or "https://" in link:
                    try:
                        photo = base64.b64encode(requests.get(link).content)
                        vals = {
                            'name': self.name,
                            'product_tmpl_id': self.id,
                            'image_1920': photo
                        }
                        self.env['product.image'].create(vals)
                    except:
                        bad_link.append(link)
                else:
                    bad_link.append(link)
            if bad_link:
                bad_string = ','.join(bad_link)
                message = "Invalid Links %s" % (bad_string)
            else:
                message = "Successful"
            self.sh_mee = message


class Productproduct(models.Model):
    _inherit = 'product.product'

    product_image_1 = fields.Char('Product Image Url')

    @api.onchange('product_image_1')
    def onchange_image(self):
        link = self.product_image_1
        if link:
            if "http://" in link or "https://" in link:
                photo = base64.b64encode(requests.get(link).content)
                val = {
                    'image_1920': photo,
                }
                return {'value': val}

    def get_image_urls(self):
        bad_link = []
        if self.sh_extra_image_url:
            if self.product_template_image_ids:
                self.product_template_image_ids.unlink()
            list_url = self.sh_extra_image_url.split(",")
            for urls in list_url:
                link = urls
                if "http://" in link or "https://" in link:
                    try:
                        photo = base64.b64encode(requests.get(link).content)
                        vals = {
                            'name': self.name,
                            'product_tmpl_id': self.product_tmpl_id.id,
                            'image_1920': photo
                        }
                        self.env['product.image'].create(vals)
                    except:
                        bad_link.append(link)
                else:
                    bad_link.append(link)
            if bad_link:
                bad_string = ','.join(bad_link)
                message = "These links are not valid %s" % (bad_string)
            else:
                message = "Successful"
