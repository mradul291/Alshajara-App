import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


APP_MODULE = "Alshajaraapp"


CUSTOM_FIELDS = {
    "Quotation": [
        {
            "fieldname": "po_creation_section",
            "fieldtype": "Section Break",
            "label": "Purchase Order Creation Details",
            "insert_after": "status",
            "collapsible": 0,
            "module": APP_MODULE,
        },
        {
            "fieldname": "po_created_by",
            "fieldtype": "Data",
            "label": "PO Created By",
            "insert_after": "po_creation_section",
            "read_only": 1,
            "allow_on_submit": 1,
            "no_copy": 1,
            "module": APP_MODULE,
        },
        {
            "fieldname": "po_created_by_name",
            "fieldtype": "Data",
            "label": "PO Created By Name",
            "insert_after": "po_created_by",
            "read_only": 1,
            "allow_on_submit": 1,
            "no_copy": 1,
            "module": APP_MODULE,
        },
        {
            "fieldname": "po_created_at",
            "fieldtype": "Datetime",
            "label": "PO Created At",
            "insert_after": "po_created_by_name",
            "read_only": 1,
            "allow_on_submit": 1,
            "no_copy": 1,
            "module": APP_MODULE,
        },
    ],
}


def sync_quotation_po_creation_audit_fields():
    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True, update=True)

    for doctype, fields in CUSTOM_FIELDS.items():
        for field in fields:
            frappe.db.set_value(
                "Custom Field",
                {"dt": doctype, "fieldname": field["fieldname"]},
                {
                    "fieldtype": field["fieldtype"],
                    "label": field["label"],
                    "options": field.get("options"),
                    "insert_after": field.get("insert_after"),
                    "read_only": field.get("read_only", 0),
                    "allow_on_submit": field.get("allow_on_submit", 0),
                    "no_copy": field.get("no_copy", 0),
                    "hidden": field.get("hidden", 0),
                    "collapsible": field.get("collapsible", 0),
                    "module": APP_MODULE,
                },
                update_modified=False,
            )

    frappe.clear_cache(doctype="Quotation")


def get_quotation_po_creation_audit_field_status():
    fields = [
        "po_creation_section",
        "po_created_by",
        "po_created_by_name",
        "po_created_at",
    ]
    meta = frappe.get_meta("Quotation")
    return {
        "meta": {fieldname: bool(meta.has_field(fieldname)) for fieldname in fields},
        "custom_fields": frappe.get_all(
            "Custom Field",
            filters={"dt": "Quotation", "fieldname": ["in", fields]},
            fields=[
                "fieldname",
                "label",
                "fieldtype",
                "options",
                "insert_after",
                "read_only",
                "allow_on_submit",
                "hidden",
            ],
            order_by="idx asc",
        ),
    }


def execute():
    sync_quotation_po_creation_audit_fields()
