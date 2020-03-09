# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def validate(doc, method):
	configuration_doctype = doc.configuration_doctype
	if configuration_doctype:
		meta = frappe.get_meta(configuration_doctype)
		for item in doc.items:
			for field in ['item_from_configuration', 'qty_from_configuration','desc_from_configuration']:
				if item.get(field) and not meta.get_field(item.get(field)):
					frappe.throw(_("""Row {0} field {1}: {2} is not a valid field in configuration doctype {3} 
						""").format(item.idx, _(item.meta.get_field(field).label),item.get(field), configuration_doctype))
			
			if item.selection_condition:
				try:
					dummy_configuration = frappe.new_doc(configuration_doctype)
					frappe.safe_eval(item.selection_condition, None, {'doc': dummy_configuration})
				except Exception as e:
					frappe.throw(_("""Row {0} invalid selection condition/python expression
						with error:{1}""").format(item.idx, str(e)))
					return