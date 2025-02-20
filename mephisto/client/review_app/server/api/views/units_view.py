#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from typing import Optional

from flask import current_app as app
from flask import request
from flask.views import MethodView
from werkzeug.exceptions import BadRequest

from mephisto.data_model.constants.assignment_state import AssignmentState
from mephisto.data_model.task import Task
from mephisto.data_model.unit import Unit


class UnitsView(MethodView):
    def get(self) -> dict:
        """
        Get workers' results (filtered by `task_id` and/or `unit_ids`, etc) -
        without full details of input/output.
        At least one filtering parameter must be specified
        """

        task_id = request.args.get("task_id")
        unit_ids: Optional[str] = request.args.get("unit_ids")

        app.logger.debug(f"Params: {task_id=}, {unit_ids=}")

        # Parse `unit_ids`
        if unit_ids:
            try:
                unit_ids: List[int] = [int(i.strip()) for i in unit_ids.split(",")]
            except ValueError:
                raise BadRequest("`unit_ids` must be a comma-separated list of integers.")

        # Validate params
        if not task_id and not unit_ids:
            raise BadRequest(
                "At least one of `task_id` or `unit_ids` parameters must be specified."
            )

        # Check if task with past `task_id` exists
        if task_id:
            Task.get(app.db, str(task_id))

        # Prepare response
        units = []
        for unit_id in unit_ids:
            unit: Unit = Unit.get(app.db, str(unit_id))

            if task_id and unit.task_id != task_id:
                continue

            if unit.db_status != AssignmentState.COMPLETED:
                continue

            try:
                unit_data = app.data_browser.get_data_from_unit(unit)
            except AssertionError:
                # In case if this is Expired Unit. It raises and axceptions
                unit_data = {}

            bonus = unit_data.get("bonus")
            review_note = unit_data.get("review_note")

            units.append(
                {
                    "id": int(unit.db_id),
                    "worker_id": int(unit.worker_id) if unit.worker_id else None,
                    "task_id": int(unit.task_id) if unit.task_id else None,
                    "pay_amount": unit.pay_amount,
                    "status": unit.db_status,
                    "creation_date": unit.creation_date.isoformat(),
                    "results": {
                        "start": unit_data.get("task_start"),
                        "end": unit_data.get("task_end"),
                        "inputs_preview": None,  # optional TODO [Review APP]
                        "outputs_preview": None,  # optional TODO [Review APP]
                    },
                    "review": {
                        "bonus": int(bonus) if bonus else None,
                        "review_note": review_note if review_note else None,
                    },
                }
            )

        return {
            "units": units,
        }
