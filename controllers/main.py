# from odoo import http
from odoo.http import request

from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from odoo.addons.sale.controllers.variant import VariantController
class CustomProductConfiguratorController(ProductConfiguratorController):
    
    def _show_advanced_configurator(self, product_id, variant_values, pricelist, handle_stock, **kw):
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

class CustomVariantController(VariantController):
        def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
            res = super(CustomVariantController, self).get_combination_info(product_template_id, product_id, combination, add_qty, pricelist_id, **kw)
            combination = request.env['product.template.attribute.value'].browse(combination)
            pricelist = self._get_pricelist(pricelist_id)
            cids = request.httprequest.cookies.get('cids', str(request.env.user.company_id.id))
            allowed_company_ids = [int(cid) for cid in cids.split(',')]
            ProductTemplate = request.env['product.template'].with_context(allowed_company_ids=allowed_company_ids)
            if 'context' in kw:
                ProductTemplate = ProductTemplate.with_context(**kw.get('context'))
            product_template = ProductTemplate.browse(int(product_template_id))
            if len(kw['parent_combination']):
                # parent_combination = request.env['product.template.attribute.value'].browse(kw.get('parent_combination'))
                parent_combination = request.env['product.template.attribute.value'].search([
                    ('product_tmpl_id', '=', product_template_id),
                    ('product_attribute_value_id','in', kw.get('parent_combination'))
                ]   )
                if parent_combination:
                    combination_indices = ','.join(str(id) for id in parent_combination.ids)
                    rev_combination_indices = ','.join(reversed(combination_indices.split(',')))
                    product = request.env['product.product'].search([
                        ('product_tmpl_id','=', product_template_id),
                        ('combination_indices','in', [combination_indices, rev_combination_indices])
                        ], limit=1)
                    if product.exists():
                        res = product_template._get_combination_info(parent_combination, int(product or 0), int(add_qty or 1), pricelist)
                        res.update({
                            'is_combination_possible': product_template._is_combination_possible(combination=parent_combination, parent_combination=parent_combination),
                            'parent_exclusions': product_template._get_parent_attribute_exclusions(parent_combination=parent_combination)
                        })
            return res
