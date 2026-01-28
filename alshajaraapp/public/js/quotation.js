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
		// Hide button for System Manager
		if (frappe.user.has_role("System Manager")) {
			return;
		}

		if (frm.doc.docstatus === 1 && frm.doc._sent === "Not Sent") {
			frm.add_custom_button(__("Mark as Sent"), function () {
				frappe.call({
					method: "alshajaraapp.api.quotation.mark_quotation_sent",
					args: {
						name: frm.doc.name,
					},
					callback() {
						frm.reload_doc();
					},
				});
			});
		}
	},
});

frappe.ui.form.on("Quotation Item", {
	rate: function (frm, cdt, cdn) {
		// wait for ERPNext pricing to finish
		setTimeout(() => {
			calculate_profit_percentage(cdt, cdn);
		}, 100);
	},
});

function calculate_profit_percentage(cdt, cdn) {
	let row = locals[cdt][cdn];

	let base_rate = flt(row.price_list_rate);
	let selling_rate = flt(row.rate);

	let profit_percentage = 0;

	if (base_rate > 0 && selling_rate > 0) {
		profit_percentage = ((selling_rate - base_rate) / base_rate) * 100;
	}

	frappe.model.set_value(cdt, cdn, "total_profit_percentage", flt(profit_percentage, 2));
}

frappe.ui.form.on("Quotation", {
	refresh(frm) {
		calculate_total_profit(frm);
	},
});

frappe.ui.form.on("Quotation Item", {
	rate: function (frm) {
		trigger_parent_profit_calc(frm);
	},
	qty: function (frm) {
		trigger_parent_profit_calc(frm);
	},
	price_list_rate: function (frm) {
		trigger_parent_profit_calc(frm);
	},
	margin_rate_or_amount: function (frm) {
		trigger_parent_profit_calc(frm);
	},
});

function trigger_parent_profit_calc(frm) {
	// wait for async pricing updates
	setTimeout(() => {
		calculate_total_profit(frm);
	}, 150);
}

function calculate_total_profit(frm) {
	let total_cost = 0;
	let total_selling = 0;

	(frm.doc.items || []).forEach((row) => {
		let qty = flt(row.qty);
		let base_rate = flt(row.price_list_rate);
		let selling_rate = flt(row.rate);

		total_cost += base_rate * qty;
		total_selling += selling_rate * qty;
	});

	let total_profit_amount = total_selling - total_cost;
	let total_profit_percentage = 0;

	if (total_cost > 0) {
		total_profit_percentage = (total_profit_amount / total_cost) * 100;
	}

	frm.set_value("total_profit_amount", flt(total_profit_amount, 2));

	frm.set_value("total_profit_percentage", flt(total_profit_percentage, 2));
}
