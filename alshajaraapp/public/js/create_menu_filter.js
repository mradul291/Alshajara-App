const ALSHAJARA_CREATE_MENU_ALLOWLIST = {
	"Sales Order": ["Sales Invoice"],
	"Sales Invoice": ["Delivery Note", "Payment"],
};

function schedule_alshajara_create_menu_filter(frm) {
	if (!frm || frm.doc.docstatus !== 1) {
		return;
	}

	const run_filter = () => filter_alshajara_create_menu(frm);

	if (frappe.after_ajax) {
		frappe.after_ajax(() => requestAnimationFrame(run_filter));
	} else {
		requestAnimationFrame(run_filter);
	}
}

function filter_alshajara_create_menu(frm) {
	const allowed_labels = ALSHAJARA_CREATE_MENU_ALLOWLIST[frm.doctype];
	if (!allowed_labels?.length || frm.doc.docstatus !== 1) {
		return;
	}

	const create_group = __("Create");
	const allowed = new Set(allowed_labels.map((label) => __(label)));
	const group = frm.page?.get_inner_group_button?.(create_group);
	if (!group?.length) {
		return;
	}

	group.find(".dropdown-item").each(function () {
		const label = decodeURIComponent($(this).attr("data-label") || "");
		if (label && !allowed.has(label)) {
			frm.remove_custom_button(label, create_group);
		}
	});

	if (group.find(".dropdown-item").length) {
		frm.page.set_inner_btn_group_as_primary(create_group);
	}
}

frappe.ui.form.on("Sales Order", {
	refresh: schedule_alshajara_create_menu_filter,
	onload_post_render: schedule_alshajara_create_menu_filter,
});

frappe.ui.form.on("Sales Invoice", {
	refresh: schedule_alshajara_create_menu_filter,
	onload_post_render: schedule_alshajara_create_menu_filter,
});
