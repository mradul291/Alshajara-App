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

frappe.ui.form.on("Opportunity", {
	before_save: function (frm) {
		sync_last_communication(frm);
	},
	onload_post_render: function (frm) {
		sync_last_communication(frm);
	},
});

function sync_last_communication(frm) {
	if (!frm.doc.notes || frm.doc.notes.length === 0) {
		frm.set_value("last_communicated_note", "");
		frm.set_value("last_communicated_date", "");
		return;
	}

	// Filter rows having added_on
	let valid_notes = frm.doc.notes.filter((row) => row.added_on);

	if (valid_notes.length === 0) {
		return;
	}

	// Sort by added_on DESC
	valid_notes.sort((a, b) => {
		return new Date(b.added_on) - new Date(a.added_on);
	});

	let latest = valid_notes[0];

	frm.set_value("last_communicated_note", latest.note || "");
	frm.set_value("last_communicated_date", latest.added_on || "");
}

frappe.ui.form.on("Opportunity Item", {
	item_code: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];

		if (!row.item_code) return;

		// Hard-coded as per your requirement
		const price_list = "Standard Selling";

		frappe.call({
			method: "frappe.client.get_value",
			args: {
				doctype: "Item Price",
				filters: {
					item_code: row.item_code,
					price_list: price_list,
					selling: 1,
				},
				fieldname: "price_list_rate",
			},
			callback: function (r) {
				if (r.message && r.message.price_list_rate != null) {
					frappe.model.set_value(cdt, cdn, "rate", r.message.price_list_rate);
				} else {
					// No price found fallback
					frappe.model.set_value(cdt, cdn, "rate", 0);
				}
			},
		});
	},
});
