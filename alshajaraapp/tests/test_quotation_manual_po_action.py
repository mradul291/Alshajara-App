import unittest
from unittest.mock import patch

import frappe

from alshajaraapp.quotation import quotation as quotation_hooks


class CapturingQuotationPurchaseOrderGenerator:
    calls = []

    def __init__(self, quotation, notify=True):
        self.quotation = quotation
        self.notify = notify
        self.duplicate_purchase_orders = []
        self.warning_messages = []
        self.skipped_messages = []
        self.__class__.calls.append((quotation, notify))

    def run(self):
        return ["PO-TEST"]


class DuplicateQuotationPurchaseOrderGenerator(CapturingQuotationPurchaseOrderGenerator):
    def run(self):
        self.duplicate_purchase_orders = ["PO-EXISTING"]
        return ["PO-EXISTING"]


def make_quotation(status="Draft", workflow_state="", docstatus=0):
    quotation = frappe._dict(
        doctype="Quotation",
        name="QTN-WORKFLOW-TEST",
        docstatus=docstatus,
        status=status,
        workflow_state=workflow_state,
    )
    quotation.check_permission = lambda permission: None
    return quotation


def fake_throw(message, exc=frappe.ValidationError, *args, **kwargs):
    raise exc(message)


class TestQuotationManualPurchaseOrderAction(unittest.TestCase):
    def setUp(self):
        CapturingQuotationPurchaseOrderGenerator.calls = []

    def run_action(self, quotation, generator=CapturingQuotationPurchaseOrderGenerator):
        with (
            patch.object(quotation_hooks.frappe, "get_doc", return_value=quotation),
            patch.object(quotation_hooks.frappe, "has_permission", return_value=True),
            patch.object(quotation_hooks.frappe, "msgprint"),
            patch.object(quotation_hooks.frappe, "throw", side_effect=fake_throw),
            patch.object(quotation_hooks, "_", side_effect=lambda value: value),
            patch.object(quotation_hooks, "get_link_to_form", side_effect=lambda doctype, name: name),
            patch.object(quotation_hooks, "QuotationPurchaseOrderGenerator", generator),
        ):
            return quotation_hooks.create_purchase_orders_from_quotation(quotation.name)

    def test_manual_action_creates_purchase_order(self):
        quotation = make_quotation()

        result = self.run_action(quotation)

        self.assertEqual(result["status"], "created")
        self.assertEqual(result["purchase_orders"], ["PO-TEST"])
        self.assertEqual(CapturingQuotationPurchaseOrderGenerator.calls, [(quotation, False)])

    def test_status_does_not_block_manual_purchase_order_creation(self):
        quotation = make_quotation(status="Submitted")

        result = self.run_action(quotation)

        self.assertEqual(result["status"], "created")
        self.assertEqual(CapturingQuotationPurchaseOrderGenerator.calls, [(quotation, False)])

    def test_workflow_state_does_not_block_manual_purchase_order_creation(self):
        quotation = make_quotation(status="Submitted", workflow_state="Pending Approval")

        result = self.run_action(quotation)

        self.assertEqual(result["status"], "created")
        self.assertEqual(result["purchase_orders"], ["PO-TEST"])

    def test_draft_quotation_can_create_purchase_order_by_manual_action(self):
        quotation = make_quotation(docstatus=0)

        result = self.run_action(quotation)

        self.assertEqual(result["status"], "created")
        self.assertEqual(CapturingQuotationPurchaseOrderGenerator.calls, [(quotation, False)])

    def test_user_without_purchase_order_create_permission_is_blocked(self):
        quotation = make_quotation()

        with (
            patch.object(quotation_hooks.frappe, "get_doc", return_value=quotation),
            patch.object(quotation_hooks.frappe, "has_permission", return_value=False),
            patch.object(quotation_hooks.frappe, "throw", side_effect=fake_throw),
            patch.object(quotation_hooks, "_", side_effect=lambda value: value),
        ):
            with self.assertRaises(frappe.PermissionError):
                quotation_hooks.create_purchase_orders_from_quotation(quotation.name)

        self.assertEqual(CapturingQuotationPurchaseOrderGenerator.calls, [])

    def test_existing_purchase_order_returns_clear_duplicate_response(self):
        quotation = make_quotation()

        result = self.run_action(quotation, generator=DuplicateQuotationPurchaseOrderGenerator)

        self.assertEqual(result["status"], "already_exists")
        self.assertEqual(result["purchase_orders"], ["PO-EXISTING"])


if __name__ == "__main__":
    unittest.main()
