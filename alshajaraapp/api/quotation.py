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

	# 2️⃣ Get next proper idx for child table
	max_idx = frappe.db.sql(
		"""
		SELECT IFNULL(MAX(idx), 0)
		FROM `tabCRM Note`
		WHERE parent = %s
		  AND parenttype = 'Quotation'
		  AND parentfield = 'notes'
		""",
		(quotation,)
	)[0][0]

	next_idx = max_idx + 1

	# 3️⃣ Insert CRM Note with correct idx
	frappe.get_doc({
		"doctype": "CRM Note",
		"parent": quotation,
		"parenttype": "Quotation",
		"parentfield": "notes",
		"idx": next_idx,              # ✅ FIXED INDEX
		"note": note,                 # keep rich text here
		"added_by": frappe.session.user,
		"added_on": current_time,
	}).insert(ignore_permissions=True)

	# 4️⃣ Store CLEAN text in quotation summary fields
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


import frappe
from frappe.utils import now_datetime, add_days

@frappe.whitelist()
def mark_quotation_sent(name):
    now = now_datetime()

    frappe.db.set_value(
        "Quotation",
        name,
        {
            "_sent": "Sent",
            "last_communication_note": "Quotation Sent",
            "last_communication_date": now,
            "next_follow_up_date": add_days(now, 1)
        }
    )

    frappe.db.commit()
