export default {
	refresh: function(frm) {
		var grid = frm.fields_dict['config_items'].grid;
		$(grid.wrapper).find('.grid-add-row').addClass('hidden')
	}
};

export const configuration_result_item = {
	form_render: function(frm, cdt, cdn) {
	    var row = locals[cdt][cdn];
		var grid = frm.fields_dict['config_items'].grid;
		if (!grid) return;
		var grid_frm = grid.grid_rows_by_docname[row.name].grid_form;
		grid_frm && grid_frm.wrapper.find(".row-actions").toggle(false);		
	},
	rate: function(frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		frappe.model.set_value(row.doctype, row.name, 'amount', row.rate * row.qty)		
	},
	amount: function(frm, cdt, cdn) {
		var total = 0;
		$.each(frm.doc.config_items || [], function (i, d) {
			total += flt(d.amount);
		});
		frm.set_value("total", total);
	}
};