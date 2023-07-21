# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    document_count = fields.Integer(
        compute="_compute_document_count",
    )

    def _compute_document_count(self):
        self.document_count = 0
        attachment_groups = self.env["ir.attachment"].read_group(
            [("res_model", "=", "hr.employee"), ("res_id", "in", self.ids)],
            ["res_id"],
            ["res_id"],
        )
        count_dict = {x["res_id"]: x["res_id_count"] for x in attachment_groups}
        for record in self:
            record.document_count = count_dict.get(record.id, 0)

    @api.model
    def check_access_rights(self, operation, raise_exception=True):
        """We need to avoid an access error that would occur when trying to access
        the user's employee record in order to view their attachments.
        This overwrite will only be necessary if the user does not have HR group."""
        if (
            not self.env.is_superuser()
            and not self.env.user.has_group("hr.group_hr_user")
            and operation == "read"
            and self._name == "hr.employee"
        ):
            if len(self) == 0:
                return True
            elif len(self) > 0 and self == self.env.user.employee_ids:
                raise_exception = False
        return super().check_access_rights(
            operation=operation, raise_exception=raise_exception
        )

    def action_get_attachment_tree_view(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("base.action_attachment")
        action["context"] = {
            "default_res_model": self._name,
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )
        action["search_view_id"] = (
            self.env.ref("hr_employee_document.ir_attachment_view_search").id,
        )
        return action
