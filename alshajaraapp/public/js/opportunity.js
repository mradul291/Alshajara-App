frappe.ui.form.on("Opportunity", {
	refresh(frm) {
		frm.custom_make_buttons = frm.custom_make_buttons || {};
	},

	make_quotation(frm) {
		frappe.model.open_mapped_doc({
			method: "erpnext.crm.doctype.opportunity.opportunity.make_quotation",
			frm: frm,
			callback(doc) {
				if (frm.doc.project && doc) {
					doc.project = frm.doc.project;
				}
			},
		});
	},
});
