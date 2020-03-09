export default {
	onload: function(frm) {
		frm.set_query('configuration_doctype', function(){
			return{
				filters:{'custom': 1}
			}
		})
	},
	configuration_doctype: function(frm, cdt, cdn){
	    if (frm.doc.configuration_doctype) frm.set_value('has_serial_no',1)
	}
};