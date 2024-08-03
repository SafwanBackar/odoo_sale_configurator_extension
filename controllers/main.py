# from odoo import http
from odoo.http import request

from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController

class CustomProductConfiguratorController(ProductConfiguratorController):
    
    def _show_advanced_configurator(self, product_id, variant_values, pricelist, handle_stock, **kw):
        # res = super(CustomProductConfiguratorController, self)._show_advanced_configurator(product_id, variant_values, pricelist, handle_stock, **kw)
        product = request.env['product.product'].browse(int(product_id))
        product_variant_list = []
        if product and len(product.product_variant_ids):
            for product_v in product.product_variant_ids:
                product_v_display_name_values = []
                for variant_val in product_v.product_template_attribute_value_ids:
                    product_v_display_name_values.append(variant_val.display_name)
                product_v_display_name = ', '.join(product_v_display_name_values)
                product_variant_list.append({'product_variant': product_v_display_name, 'qty': product_v.qty_available, 'forcasted_qty': product_v.virtual_available})
        combination = request.env['product.template.attribute.value'].browse(variant_values)
        add_qty = float(kw.get('add_qty', 1))

        no_variant_attribute_values = combination.filtered(
            lambda product_template_attribute_value: product_template_attribute_value.attribute_id.create_variant == 'no_variant'
        )
        if no_variant_attribute_values:
            product = product.with_context(no_variant_attribute_values=no_variant_attribute_values)

        return request.env['ir.ui.view']._render_template("sale_product_configurator.optional_products_modal", {
            'product': product,
            'product_variants': product_variant_list,
            'combination': combination,
            'add_qty': add_qty,
            'parent_name': product.name,
            'variant_values': variant_values,
            'pricelist': pricelist,
            'handle_stock': handle_stock,
            'already_configured': kw.get("already_configured", False),
            'mode': kw.get('mode', 'add'),
            'product_custom_attribute_values': kw.get('product_custom_attribute_values', None),
            'no_attribute': kw.get('no_attribute', False),
            'custom_attribute': kw.get('custom_attribute', False)
        })
