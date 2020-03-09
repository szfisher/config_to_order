# -*- coding: utf-8 -*-
# Copyright (c) 2019, 	9t9it and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def delete_configuration_doc(sales_order, method):
	"""Called when Sales Order is deleted"""
	configuration_docs = [[item.configuration_doctype,item.configuration_docname] for 
								item in sales_order.items if item.configuration_docname]
	for configuration_doc in configuration_docs:
		frappe.delete_doc(configuration_doc[0], configuration_doc[1], force =1, ignore_permissions = 1)