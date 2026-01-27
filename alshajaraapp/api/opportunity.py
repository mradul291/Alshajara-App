import frappe
from erpnext.crm.doctype.opportunity.opportunity import make_quotation as erp_make_quotation

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
    quotation = erp_make_quotation(source_name, target_doc)

    opportunity = frappe.get_doc("Opportunity", source_name)

    quotation.project_capacity = opportunity.project_capacity
    quotation.capacity_unit = opportunity.capacity_unit

    return quotation
