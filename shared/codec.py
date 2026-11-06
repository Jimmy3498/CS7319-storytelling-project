"""Strict structural decoding for fixture/contracts; NOT business or privacy validation."""

import json
import math
from dataclasses import MISSING, fields, is_dataclass
from enum import Enum
from types import UnionType
from typing import Union, get_args, get_origin, get_type_hints


def decode(value, expected_type):
    origin, args = get_origin(expected_type), get_args(expected_type)
    if origin in (Union, UnionType):
        for candidate in args:
            try:
                return decode(value, candidate)
            except (TypeError, ValueError):
                continue
        raise ValueError("Value does not match the declared union")
    if expected_type is type(None):
        if value is not None:
            raise ValueError("Expected null")
        return None
    if origin is tuple:
        if not isinstance(value, (list, tuple)):
            raise ValueError("Expected array")
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(decode(item, args[0]) for item in value)
        if len(value) != len(args):
            raise ValueError("Tuple length mismatch")
        return tuple(decode(item, kind) for item, kind in zip(value, args))
    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type(value)
    if is_dataclass(expected_type):
        if not isinstance(value, dict):
            raise ValueError("Expected typed object")
        known = {field.name: field for field in fields(expected_type)}
        if value.keys() - known.keys():
            raise ValueError("Unexpected object fields")
        hints = get_type_hints(expected_type)
        result = {}
        for name, field in known.items():
            if name in value:
                result[name] = decode(value[name], hints[name])
            elif field.default is MISSING and field.default_factory is MISSING:
                raise ValueError(f"Missing required field: {name}")
        return expected_type(**result)
    if expected_type is float:
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Expected finite number")
        return float(value)
    if expected_type in (str, int, bool):
        if type(value) is not expected_type:
            raise ValueError("Incorrect scalar type")
        return value
    raise TypeError("Unsupported decoding type")


def load_json(text: str):
    if len(text.encode("utf-8")) > 1024 * 1024:
        raise ValueError("JSON exceeds structural allowance")

    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON field")
            result[key] = value
        return result

    def reject_constant(_):
        raise ValueError("Non-finite JSON constant")

    return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
