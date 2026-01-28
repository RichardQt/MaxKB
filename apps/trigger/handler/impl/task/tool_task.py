# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： application_task.py
    @date：2026/1/14 19:14
    @desc:
"""
import json
import time
import traceback

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from common.utils.logger import maxkb_logger
from common.utils.rsa_util import rsa_long_decrypt
from common.utils.tool_code import ToolExecutor
from knowledge.models.knowledge_action import State
from tools.models import Tool
from trigger.handler.base_task import BaseTriggerTask
from trigger.models import TaskRecord


def get_reference(fields, obj):
    for field in fields:
        value = obj.get(field)
        if value is None:
            return None
        else:
            obj = value
    return obj


def get_field_value(value, kwargs):
    source = value.get('source')
    if source == 'custom':
        return value.get('value')
    else:
        return get_reference(value.get('value'), kwargs)


def _coerce_by_type(field_type, raw):
    if raw is None:
        return None
    t = (field_type or "").lower()

    if t in ("string", "str", "text"):
        return str(raw)
    if t in ("int", "integer"):
        return int(raw)
    if t in ("float", "number", "double"):
        return float(raw)
    if t in ("bool", "boolean"):
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, (int, float)):
            return bool(raw)
        if isinstance(raw, str):
            v = raw.strip().lower()
            if v in ("true", "1", "yes", "y", "on"):
                return True
            if v in ("false", "0", "no", "n", "off"):
                return False
        raise ValueError(f"Cannot coerce {raw!r} to bool")
    if t in ("list", "array"):
        if isinstance(raw, list):
            return raw
        if isinstance(raw, tuple):
            return list(raw)
        raise ValueError(f"Cannot coerce {raw!r} to list")
    if t in ("dict", "object", "json"):
        if isinstance(raw, dict):
            return raw
        raise ValueError(f"Cannot coerce {raw!r} to dict")

    return raw


def get_tool_execute_parameters(input_field_list, parameter_setting, kwargs):
    type_map = {f.get("name"): f.get("type") for f in (input_field_list or []) if f.get("name")}

    parameters = {}
    for key, value in parameter_setting.items():
        raw = get_field_value(value, kwargs)
        parameters[key] = _coerce_by_type(type_map.get(key), raw)
    return parameters


def get_loop_workflow_node(node_list):
    result = []
    for item in node_list:
        if item.get('type') == 'loop-node':
            for loop_item in item.get('loop_node_data') or []:
                for inner_item in loop_item.values():
                    result.append(inner_item)
    return result


def get_workflow_state(details):
    node_list = details.values()
    all_node = [*node_list, *get_loop_workflow_node(node_list)]
    err = any([True for value in all_node if value.get('status') == 500 and not value.get('enableException')])
    if err:
        return State.FAILURE
    return State.SUCCESS


class ToolTask(BaseTriggerTask):
    def support(self, trigger_task, **kwargs):
        return trigger_task.get('source_type') == 'TOOL'

    def execute(self, trigger_task, **kwargs):
        parameter_setting = trigger_task.get('parameter')
        tool_id = trigger_task.get('source_id')
        task_record_id = uuid.uuid7()

        TaskRecord(
            id=task_record_id,
            trigger_id=trigger_task.get('trigger'),
            trigger_task_id=trigger_task.get('id'),
            source_type="TOOL",
            source_id=tool_id,
            task_record_id=task_record_id,
            meta={},
            state=State.STARTED
        ).save()

        start_time = time.time()
        try:
            tool = QuerySet(Tool).filter(id=tool_id).first()
            parameters = get_tool_execute_parameters(tool.input_field_list, parameter_setting, kwargs)
            init_params_default_value = {i["field"]: i.get('default_value') for i in tool.init_field_list}

            if tool.init_params is not None:
                all_params = init_params_default_value | json.loads(rsa_long_decrypt(tool.init_params)) | parameters
            else:
                all_params = init_params_default_value | parameters
            executor = ToolExecutor()
            result = executor.exec_code(tool.code, all_params)

            maxkb_logger.info(f"Tool execution result: {result}")

            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=State.SUCCESS,
                run_time=time.time() - start_time
            )
        except Exception as e:
            maxkb_logger.error(f"Tool execution error: {traceback.format_exc()}")
            QuerySet(TaskRecord).filter(id=task_record_id).update(
                state=State.FAILURE,
                run_time=time.time() - start_time
            )
