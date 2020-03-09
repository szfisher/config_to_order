# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
import json
import frappe.utils
from frappe.utils import cstr, flt, getdate, comma_and, cint, nowdate, add_days
from frappe import _
from erpnext.stock.get_item_details import get_item_details

def get_bom_items_as_dict(bom, company, qty=1, fetch_exploded=1, include_non_stock_items=False):
	item_dict = {}
	# Did not use qty_consumed_per_unit in the query, as it leads to rounding loss
	query = """select
				bom_item.item_code,
				bom_item.idx,
				item.item_name,
				sum(bom_item.{qty_field}/ifnull(bom.quantity, 1)) * %(qty)s as qty,
				item.description,
				item.image,
				item.stock_uom,
				item.allow_alternative_item,
				item_default.default_warehouse,
				item_default.expense_account as expense_account,
				item_default.buying_cost_center as cost_center
				{select_columns}
			from
				`tab{table}` bom_item
				JOIN `tabBOM` bom ON bom_item.parent = bom.name
				JOIN `tabItem` item ON item.name = bom_item.item_code
				LEFT JOIN `tabItem Default` item_default
					ON item_default.parent = item.name and item_default.company = %(company)s
			where
				bom_item.docstatus < 2
				and bom.name = %(bom)s
				and item.is_stock_item in (1, {is_stock_item})
				{where_conditions}
				group by item_code, stock_uom {groupby_columns}
				order by idx"""
	is_stock_item = 0 if include_non_stock_items else 1
	if cint(fetch_exploded):
		query = query.format(table="BOM Explosion Item",
			where_conditions="",
			is_stock_item=is_stock_item,
			qty_field="stock_qty",
			select_columns = """, bom_item.source_warehouse, bom_item.operation, bom_item.include_item_in_manufacturing,
				(Select idx from `tabBOM Item` where item_code = bom_item.item_code and parent = %(parent)s limit 1) as idx,
				  bom_item.selection_condition, bom_item.item_from_configuration, bom_item.qty_from_configuration,
				  bom_item.desc_from_configuration""",
			groupby_columns = """, bom_item.operation""")

		items = frappe.db.sql(query, { "parent": bom, "qty": qty, "bom": bom, "company": company }, as_dict=True)
	else:
		query = query.format(table="BOM Item", where_conditions="", is_stock_item=is_stock_item,
			qty_field="stock_qty",
			select_columns = """, bom_item.uom, bom_item.conversion_factor, bom_item.source_warehouse, bom_item.idx, 
							 bom_item.operation, bom_item.include_item_in_manufacturing,
							  bom_item.selection_condition, bom_item.item_from_configuration, 
							  bom_item.qty_from_configuration,bom_item.desc_from_configuration""",
			groupby_columns = """, bom_item.operation""")
		items = frappe.db.sql(query, { "qty": qty, "bom": bom, "company": company }, as_dict=True)

	for item in items:
		key = (item.item_code)
		if item.operation:
			key = (item.item_code, item.operation)

		if key in item_dict:
			item_dict[key]["qty"] += flt(item.qty)
		else:
			item_dict[key] = item

	return item_dict

@frappe.whitelist()
def get_configuration_result(bom_no, fetch_exploded, configuration_doctype, configuration_docname, args = {}):
    '''set required_items for production to keep track of reserved qty
    args "company" : args.get('company'),
            "customer": args.get('customer'),
            "conversion_rate": args.get('conversion_rate') or 1.0,
            "selling_price_list": args.get('selling_price_list'),
            "price_list_currency": args.get('price_list_currency'),
            "plc_conversion_rate": args.get('plc_conversion_rate') or 1.0,
            "doctype": args.get('doctype'),
            "name": args.get('name'),
            "transaction_date": args.get('transaction_date'),
            "ignore_pricing_rule": args.get('ignore_pricing_rule'),
            "project": args.get('project')
    '''
    def check_selection_condition(configuration, bom_item):
        ret = False
        print(configuration, bom_item)
        selection_condition = bom_item.get('selection_condition')
        item_from_configuration = bom_item.get('item_from_configuration')
        if not configuration or not (item_from_configuration or selection_condition):
            ret = True
        elif item_from_configuration:
            ret = configuration.get(item_from_configuration) == bom_item.item_code
        elif selection_condition:
            ret = frappe.safe_eval(selection_condition, None, {'doc':configuration})

        return ret

    def get_qty_or_desc(configuration, bom_item, bom_field, config_field):
        config_field = bom_item.get(config_field)
        if not configuration or not config_field:
            return bom_item.get(bom_field)
        elif config_field:
            return configuration.get(config_field) or bom_item.get(bom_field)

    def update_item_detail(item_code, config_item):
        args.update({"item_code": item_code})
        item_detail = get_item_details(args)
        for field in ['valuation_rate', 'pricing_rule', 'discount_percentage', 'discount_amount', 'price_list_rate',
                      'stock_qty','uom']:
            config_item.update({field: item_detail.get(field)})
        config_item.update({'rate': item_detail.get('rate') or config_item.get('price_list_rate') or 0})
        config_item.update({'amount': config_item.get('rate') * config_item.get('qty')})

    args = frappe._dict(json.loads(args))
    item_dict = get_bom_items_as_dict(bom_no, args.get('company'), qty = 1, fetch_exploded = fetch_exploded)

    configuration = frappe.get_doc(configuration_doctype, configuration_docname)
    configuration_result = frappe.new_doc('Configuration Result')
    configuration_result.reference_doctype = configuration_doctype
    configuration_result.reference_docname = configuration_docname
    configuration_result.set_new_name()
    for item in sorted(item_dict.values(), key=lambda d: d['idx'] or 9999):
        if check_selection_condition(configuration, item):
            config_item = {
                'item_code': item.item_code,
                'item_name': item.item_name,                
                'description': get_qty_or_desc(configuration, item, 'description', 'desc_from_configuration'),
                'qty': get_qty_or_desc(configuration, item, 'qty', 'qty_from_configuration')
            }
            update_item_detail(item.item_code, config_item)
            configuration_result.append('config_items', config_item )
    return configuration_result

def get_configuration_fields(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	"""get relevant fields of the configuration doctype"""

	def check(f):
		return not txt or [t for t in [f.fieldname,f.label,_(f.fieldname), _(f.label)] if txt in t]

	fields = []
	doctype = filters.get('configuration_doctype')
	field_types = filters.get('field_types', [])
	if doctype:
		meta = frappe.get_meta(doctype)
		fields = [[f.fieldname, _(f.fieldname), _(f.label)] for f in meta.fields if (not field_types or f.fieldtype in field_types) and check(f)]

	return fields
	
def get_configuration_docname(doctype=None, txt=None, searchfield=None, start=None, page_len=None, filters=None):
	"""get relevant fields of the configuration doctype"""
		
	return frappe.db.sql("""select soi.configuration_docname, so.name, so.customer from `tabSales Order Item` soi
		inner join `tabSales Order` so on soi.parent=so.name where 
		soi.configuration_doctype = %(configuration_doctype)s  and soi.configuration_docname is not null 
		and (soi.configuration_docname like %(txt)s or so.name like %(txt)s)""", 
		{'configuration_doctype':filters.get('configuration_doctype'), 
		 'txt': "%%%s%%" % txt})
