frappe.ui.form.make_control = function (opts) {
	if (opts.df.fieldtype =='Data' && opts.df.options==='custom query'){
		opts.df.fieldtype='Link';
		opts.df.ignore_link_validation= true;
		opts.df.only_select = true;
		opts.with_link_btn = false;
	};
	var control_class_name = "Control" + opts.df.fieldtype.replace(/ /g, "");
	if(frappe.ui.form[control_class_name]) {
		return new frappe.ui.form[control_class_name](opts);
	} else {
		// eslint-disable-next-line
		console.log("Invalid Control Name: " + opts.df.fieldtype);
	}
};

frappe.ui.form.update_calling_link = (newdoc) => {
	if (!frappe._from_link) return;
	var doc = frappe.get_doc(frappe._from_link.doctype, frappe._from_link.docname);

	let is_valid_doctype = () => {
		if (frappe._from_link.df.fieldtype==='Link') {
			return newdoc.doctype === frappe._from_link.df.options;
		} else {
			// dynamic link, type is dynamic
			return newdoc.doctype === doc[frappe._from_link.df.options];
		}
	};

	if (is_valid_doctype()) {
		// set value
		if (doc && doc.parentfield) {
			//update values for child table
			$.each(frappe._from_link.frm.fields_dict[doc.parentfield].grid.grid_rows, function (index, field) {
				if (field.doc && field.doc.name === frappe._from_link.docname) {
					frappe._from_link.set_value(newdoc.name);
				}
			});
		} else {
			frappe._from_link.set_value(newdoc.name);
		}

		// refresh field
		frappe._from_link.refresh();
		
		// if from form, switch
		if (frappe._from_link.frm) {
			var link = frappe._from_link;		
			frappe.set_route("Form",
				frappe._from_link.frm.doctype, frappe._from_link.frm.docname)
				.then(() => {
					frappe.utils.scroll_to(frappe._from_link_scrollY);
					var d = link && link.doc;
					d && link.frm.fields_dict[d.parentfield].grid.grid_rows_by_docname[d.name].show_form();
				});
		}

		frappe._from_link = null;
	}
}