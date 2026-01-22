frappe.ui.form.on("Sales Invoice", {
	refresh(frm) {
		calculate_total_received(frm);
	},
	grand_total(frm) {
		calculate_total_received(frm);
	},
	outstanding_amount(frm) {
		calculate_total_received(frm);
	},
});

function calculate_total_received(frm) {
	let grand_total = flt(frm.doc.grand_total);
	let outstanding_amount = flt(frm.doc.outstanding_amount);

	let total_received = 0;

	if (grand_total > 0) {
		total_received = grand_total - outstanding_amount;
	}

	frm.set_value("total_received", flt(total_received, 2));
}
