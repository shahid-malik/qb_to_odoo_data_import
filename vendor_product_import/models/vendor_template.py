from odoo import models, fields


class VendorTemplate(models.Model):
    _name = 'mediod.vendor.template'

    name = fields.Char(string="Template Name", required=True)
    vendor = fields.Many2one('res.partner', string="Vendor", required=True)
    sample_file = fields.Binary(string="Sample CSV")
    vendor_lines = fields.One2many(comodel_name='mediod.vendor.template.line', inverse_name='vendor_template')


class VendorTemplateLine(models.Model):
    _name = 'mediod.vendor.template.line'

    odoo_field = fields.Char(string="Odoo Field")
    csv_field = fields.Char(string='CSV Field')
    # have_duplicate = fields.Binary(string="Contain Duplicate?")
    is_unique = fields.Boolean(string="Is Unique?", default=False)
    have_duplicate = fields.Boolean(string="Having Duplicate?", default=False)
    has_unit = fields.Boolean("Having Unit?", default=False)
    vendor_template = fields.Many2one('mediod.vendor.template', 'Vendor Template')


class VendorProductImport(models.Model):
    _name = 'mediod.vendor.product.import'

    vendor_template = fields.Many2one('mediod.vendor.template', 'Vendor Template')
    input_file = fields.Binary(string="Sample CSV")
