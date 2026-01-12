# import frappe
# from frappe.utils import now
# from frappe import _

# @frappe.whitelist()
# def add_quotation_note(quotation, note):
# 	if not quotation or not note:
# 		frappe.throw(_("Missing quotation or note"))

# 	# Permission check (still important)
# 	doc = frappe.get_doc("Quotation", quotation)
# 	doc.check_permission("read")

# 	# Direct DB insert into child table
# 	frappe.get_doc({
# 		"doctype": "CRM Note",
# 		"parent": quotation,
# 		"parenttype": "Quotation",
# 		"parentfield": "notes",
# 		"note": note,
# 		"added_by": frappe.session.user,
# 		"added_on": now(),
# 	}).insert(ignore_permissions=True)

# 	return True

import frappe
from frappe.utils import now, strip_html
from frappe import _


@frappe.whitelist()
def add_quotation_note(quotation, note, next_follow_up_date=None):
	if not quotation or not note:
		frappe.throw(_("Missing quotation or note"))

	# Permission check
	doc = frappe.get_doc("Quotation", quotation)
	doc.check_permission("read")

	current_time = now()

	# 1️⃣ Clean note for summary fields (plain text only)
	clean_note = strip_html(note).strip()

	# 2️⃣ Insert full HTML note in child table (KEEP HTML here)
	frappe.get_doc({
		"doctype": "CRM Note",
		"parent": quotation,
		"parenttype": "Quotation",
		"parentfield": "notes",
		"note": note,  # keep rich text here
		"added_by": frappe.session.user,
		"added_on": current_time,
	}).insert(ignore_permissions=True)

	# 3️⃣ Store CLEAN text in communication summary fields
	frappe.db.set_value(
		"Quotation",
		quotation,
		{
			"last_communication_note": clean_note,
			"last_communication_date": current_time,
			"next_follow_up_date": next_follow_up_date,
		},
		update_modified=False
	)

	return True
