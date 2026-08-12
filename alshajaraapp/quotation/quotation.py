import frappe
from frappe import _
from frappe.utils import get_link_to_form

from alshajaraapp.quotation.purchase_order_generator import QuotationPurchaseOrderGenerator


def log_auto_po_debug(message, *args):
    try:
        frappe.logger("alshajaraapp.quotation_auto_po").info(message, *args)
    except Exception:
        pass


def get_existing_purchase_orders_for_quotation(quotation):
    if not quotation:
        return []

    doc = frappe.get_doc("Quotation", quotation)
    doc.check_permission("read")
    return QuotationPurchaseOrderGenerator(doc, notify=False).get_existing_purchase_orders()


def create_purchase_orders_for_shortages(doc, method=None):
    """Legacy hook retained as a no-op; PO creation is now manual."""
    log_auto_po_debug(
        "Quotation automatic PO creation is disabled for %s with docstatus %s",
        doc.name,
        doc.docstatus,
    )
    return


@frappe.whitelist()
def get_manual_purchase_order_status(quotation):
    """Return existing Quotation-linked Purchase Orders for client button state."""
    purchase_orders = get_existing_purchase_orders_for_quotation(quotation)
    return {
        "has_purchase_orders": bool(purchase_orders),
        "purchase_orders": purchase_orders,
    }


@frappe.whitelist()
def create_purchase_orders_from_quotation(quotation):
    """Create Purchase Orders from a Quotation by explicit user action."""
    if not quotation:
        frappe.throw(_("Quotation is required."))

    doc = frappe.get_doc("Quotation", quotation)
    doc.check_permission("read")

    if not frappe.has_permission("Purchase Order", "create"):
        frappe.throw(_("You do not have permission to create Purchase Orders."), frappe.PermissionError)

    generator = QuotationPurchaseOrderGenerator(doc, notify=False)
    purchase_orders = generator.run()

    if generator.duplicate_purchase_orders:
        links = [
            get_link_to_form("Purchase Order", po_name)
            for po_name in generator.duplicate_purchase_orders
        ]
        message = _("Purchase Order already exists for this Quotation: {0}").format(", ".join(links))
        frappe.msgprint(message, indicator="orange")
        return {
            "status": "already_exists",
            "purchase_orders": generator.duplicate_purchase_orders,
            "message": message,
        }

    if not purchase_orders:
        message = _("No Purchase Order was created. Check stock, warehouse, and supplier setup for shortage items.")
        frappe.msgprint(message, indicator="orange")
        return {
            "status": "no_purchase_order_created",
            "purchase_orders": [],
            "message": message,
            "warnings": generator.warning_messages,
            "skipped": generator.skipped_messages,
        }

    links = [get_link_to_form("Purchase Order", po_name) for po_name in purchase_orders]
    message = _("Created Purchase Order: {0}").format(", ".join(links))
    frappe.msgprint(message, indicator="green")

    return {
        "status": "created",
        "purchase_orders": purchase_orders,
        "message": message,
        "warnings": generator.warning_messages,
        "skipped": generator.skipped_messages,
    }
