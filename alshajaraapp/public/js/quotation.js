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
