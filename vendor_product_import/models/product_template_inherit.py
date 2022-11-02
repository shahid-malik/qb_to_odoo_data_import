from odoo import models, fields


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    product_family_id = fields.Integer('Part Family ID')
    product_brand_id = fields.Char('Brand Id')
    product_brand_name = fields.Char('Brand Name')
    product_category_id = fields.Char('Category ID')
    image_metaname = fields.Char('Image Name')
    product_image = fields.Char('Image Family Medium')
    website_description = fields.Char('Description')
    asin = fields.Char("Asin")
    upc = fields.Char("Upc")

    case_size = fields.Integer('Case Size')
    product_size = fields.Float("Product Size")
    notes = fields.Text("Notes")
    # whole sale pricing
    ws_each = fields.Float("Each Price")
    ws_case = fields.Float("Case Price")
    # MSRP Pricing
    msrp_each = fields.Float("Each Price")
    msrp_case = fields.Float("Case Price")
    # Dimensions
    length = fields.Float("Length")
    width = fields.Float("Width")
    height = fields.Float("Height")
    # Weight in Kilograms
    ctn_weight = fields.Float("CTN Weight")
    formulation_sg = fields.Float("Formulation with SG")
    rounded_kg = fields.Float("Rounded Kg")
    gross_weight = fields.Float("Gross Weight EA")
    # Weight in Lbs
    container_weight_lbs = fields.Float("Container Weight")
    rounded_lbs = fields.Float("Rounded Lbs")
    gross_weight_lbs = fields.Float("Gross Weight EA")
    # Content
    liquid_metric = fields.Float("Liquid Metric (L)")
    liquid_imp = fields.Float("Liquid Imp (Gal)")
    # Net weight
    weight_metric = fields.Float("Weight Metric (kg)")
    weight_imp_lbs = fields.Float("Weight Imp (Lbs)")
