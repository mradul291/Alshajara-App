import frappe
from frappe.utils import now, strip_html, now_datetime, add_days , getdate
from frappe import _
import io
from frappe.utils.file_manager import save_file
from barcode import Code128
from barcode.writer import ImageWriter

def generate_document_barcode(doc, method):
    """
    Generic barcode generator for any document.
    Uses doc.name and attaches barcode to the same doctype.
    """

    if not hasattr(doc, "barcode") or doc.barcode:
        return

    barcode_value = doc.name

    buffer = io.BytesIO()
    Code128(barcode_value, writer=ImageWriter()).write(buffer)

    filename = f"{barcode_value}.png"

    file_doc = save_file(
        fname=filename,
        content=buffer.getvalue(),
        dt=doc.doctype,
        dn=doc.name,
        folder="Home/Attachments",
        is_private=0
    )

    frappe.db.set_value(
        doc.doctype,
        doc.name,
        "barcode",
        file_doc.file_url
    )


def reset_document_barcode_on_amend(doc, method):
    """
    Reset barcode if document is created via mapping
    (PO → PI / PR etc.)
    """

    if hasattr(doc, "barcode"):
        doc.barcode = None

    if hasattr(doc, "barcode_preview"):
        doc.barcode_preview = None
