export default {
	onload: function(frm) {
		frm.set_query("item_from_configuration","items", ()=>{return set_query(frm, ['Data','Select','Link'])});
		frm.set_query("qty_from_configuration","items",  ()=>{ return set_query(frm, ['Int','Float'])});
		frm.set_query("desc_from_configuration","items", ()=>{ return set_query(frm, ['Data','Select','Link'])});
	}
}

var set_query = function(frm, field_types){
	return {
		query: "config_to_order.api.variant_configuration.get_configuration_fields",
		filters: {
			configuration_doctype:frm.doc.configuration_doctype,
			field_types: field_types
		}
	}	
}