# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """The base module in ir.attachment removes records to which you do not have
        permission, which is correct, but in the case of hr.employee not exactly,
        since you should have access to the user's employee attachments.
        To avoid creating ACLS related to hr.employee that would cause side effects,
        we will apply sudo to get records when necessary.
        This overwrite will only be necessary if the user does not have HR group."""
        res = super()._search(
            args=args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )
        if (
            not self.env.user.has_group("hr.group_hr_user")
            and len(res) == 0
            and not self.env.context.get("skip_override_ir_attachment_search")
        ):
            args_to_check_0 = False
            args_to_check_1 = False
            for arg in args:
                if isinstance(args, (list)):
                    if (
                        arg[0] == "res_model"
                        and arg[1] == "="
                        and arg[2] == "hr.employee"
                    ):
                        args_to_check_0 = True
                    elif (
                        arg[0] == "res_id"
                        and arg[1] == "="
                        and arg[2] == self.env.user.employee_id.id
                    ):
                        args_to_check_1 = True
            if args_to_check_0 and args_to_check_1:
                _self = self.sudo().with_context(
                    skip_override_ir_attachment_search=True
                )
                return super(IrAttachment, _self)._search(
                    args=args,
                    offset=offset,
                    limit=limit,
                    order=order,
                    count=count,
                    access_rights_uid=access_rights_uid,
                )
        return res
