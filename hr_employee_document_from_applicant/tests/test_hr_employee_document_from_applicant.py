# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.addons.base.tests.common import BaseCommon


class TestHrEmployeeDocumentFromApplicant(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.applicant = cls.env["hr.applicant"].create(
            {
                "partner_name": "Test Application",
                "email_from": "laurie.poiret@aol.ru",
            }
        )

    @classmethod
    def _create_attachment(self, applicant_id):
        return (
            self.env["ir.attachment"]
            .sudo()
            .create(
                [
                    {
                        "res_model": applicant_id._name,
                        "res_id": applicant_id.id,
                        "datas": base64.b64encode(b"My attachment"),
                        "name": "doc.txt",
                    }
                ]
            )
        )

    def test_create_employee_from_applicant(self):
        attachment = self._create_attachment(self.applicant)
        res = self.applicant.create_employee_from_applicant()
        employee = self.env[res["res_model"]].browse(res["res_id"])
        employee_attachments = self.env["ir.attachment"].search(
            [
                ("res_model", "=", employee._name),
                ("res_id", "=", employee.id),
            ]
        )
        self.assertEqual(len(employee_attachments), 1)
        self.assertEqual(employee_attachments.name, attachment.name)
