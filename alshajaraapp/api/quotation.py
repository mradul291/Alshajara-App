import frappe
from frappe.utils import now, strip_html, now_datetime, add_days , getdate
from frappe import _
import io
from frappe.utils.file_manager import save_file
from barcode import Code128
from barcode.writer import ImageWriter
from erpnext.selling.doctype.quotation.quotation import make_sales_order as core_make_sales_order

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

def set_custom_quotation_name(doc, method):
    # Safety: do not override if already named
    if doc.name and not doc.name.startswith("New"):
        return

    # 1. Company Code (static as per requirement)
    company_code = "3S"

    # 2. Date parts
    if not doc.transaction_date:
        frappe.throw("Transaction Date is required to generate Quotation number")

    date = getdate(doc.transaction_date)
    year = date.strftime("%y")
    month = date.strftime("%m")
    day = date.strftime("%d")

    # 3. Collect UNIQUE brand abbreviations from items
    if not doc.items:
        frappe.throw("At least one item is required to generate Quotation number")

    brand_abbrs = set()

    for item in doc.items:
        if not item.brand:
            frappe.throw("Brand is required for all items in Quotation")

        abbreviation = frappe.db.get_value(
            "Brand",
            item.brand,
            "abbreviation"
        )

        if not abbreviation:
            frappe.throw(
                f"Abbreviation is missing for Brand: {item.brand}"
            )

        brand_abbrs.add(abbreviation.strip().upper())

    # Deterministic order
    brand_abbr_str = "".join(sorted(brand_abbrs))

    # 4. Prefix
    prefix = f"{company_code}{year}{brand_abbr_str}{month}{day}"

    # 5. Running series (last 2 digits)
    last_name = frappe.db.sql(
        """
        SELECT name
        FROM `tabQuotation`
        WHERE name LIKE %s
        ORDER BY name DESC
        LIMIT 1
        """,
        (prefix + "%",),
        as_dict=True
    )

    if last_name:
        last_series = int(last_name[0].name[-2:])
        new_series = last_series + 1
    else:
        new_series = 1

    series_str = str(new_series).zfill(2)

    # 6. Final name
    doc.name = f"{prefix}{series_str}"

def generate_quotation_barcode(doc, method):
    """
    Generates barcode image using Quotation name
    and attaches it to the Quotation document
    """

    # Do not regenerate if already exists
    if doc.barcode:
        return

    barcode_value = doc.name  # 🔑 Use generated quotation name

    # Generate barcode image in memory
    buffer = io.BytesIO()
    Code128(barcode_value, writer=ImageWriter()).write(buffer)

    filename = f"{barcode_value}.png"

    # Save file in Frappe
    file_doc = save_file(
        fname=filename,
        content=buffer.getvalue(),
        dt="Quotation",
        dn=doc.name,
        folder="Home/Attachments",
        is_private=0
    )

    # Update quotation with barcode file
    frappe.db.set_value(
        "Quotation",
        doc.name,
        "barcode",
        file_doc.file_url
    )

@frappe.whitelist()
def make_sales_order_with_shipping_status(source_name, target_doc=None):
    """
    Create Sales Order from Quotation
    and sync Shipping Status
    """

    # Call core ERPNext function
    sales_order = core_make_sales_order(source_name, target_doc)

    # Fetch Shipping Status from Quotation
    shipping_status = frappe.db.get_value(
        "Quotation",
        source_name,
        "shipping_status"
    )

    if shipping_status:
        sales_order.shipping_status = shipping_status

    return sales_order
