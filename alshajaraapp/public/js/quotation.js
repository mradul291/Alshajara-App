frappe.ui.form.on("Quotation", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__("+ Add Note"), () => {
				frm.trigger("open_add_note_dialog");
			});
		}
	},

	open_add_note_dialog(frm) {
		let d = new frappe.ui.Dialog({
			title: __("Add Note"),
			fields: [
				{
					label: __("Note"),
					fieldname: "note",
					fieldtype: "Text Editor",
					reqd: 1,
				},
			],
			primary_action_label: __("Add"),
			primary_action(values) {
				frappe.call({
					method: "alshajaraapp.api.quotation.add_quotation_note",
					args: {
						quotation: frm.doc.name,
						note: values.note,
					},
					freeze: true,
					callback() {
						d.hide();
						frm.reload_doc();
					},
				});
			},
		});

		d.show();
	},
});

frappe.ui.form.on("Quotation", {
	refresh(frm) {
		if (frm.doc.docstatus === 1 && frm.doc._sent === "Not Sent") {
			frm.add_custom_button(__("Mark as Sent"), function () {
				frappe.call({
					method: "alshajaraapp.api.quotation.mark_quotation_sent",
					args: {
						name: frm.doc.name,
					},
					callback: function () {
						frm.reload_doc();
					},
				});
			});
		}
	},
});
