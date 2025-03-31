from dataclasses import is_dataclass, fields
import enum
from typing import Any
import yaml


def strip_nulls_from_dataclass(dc):
    """
    If there are trailing empty bytes defined, this function strips them.
    """
    if not is_dataclass(dc):
        return dc

    for f in fields(dc):
        value = getattr(dc, f.name)
        if isinstance(value, str):
            setattr(dc, f.name, value.rstrip("\x00"))
        elif is_dataclass(value):
            strip_nulls_from_dataclass(value)
        elif isinstance(value, list):
            pass
    return dc


def dataclass_to_dict(obj: Any) -> Any:
    """
    Recursively convert dataclasses to a dict
    """
    if isinstance(obj, enum.Enum):
        return obj.name

    if is_dataclass(obj):
        result = {}
        for f in fields(obj):
            value = getattr(obj, f.name)
            result[f.name] = dataclass_to_dict(value)
        return result

    if isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]

    if isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}

    return obj


class Config:
    """
    Reads config.yaml
    """

    _instance = None

    def __new__(cls, config_path="config.yaml"):
        if cls._instance is None:
            with open(config_path, "r") as file:
                cls._instance = super(Config, cls).__new__(cls)
                cls._instance.config_data = yaml.safe_load(file)
        return cls._instance

    def get(self, key, default=None):
        keys = key.split(".")
        data = self.config_data
        for k in keys:
            data = data.get(k, default)
            if data is default:
                break
        return data
