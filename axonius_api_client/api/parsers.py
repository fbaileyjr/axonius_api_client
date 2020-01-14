# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .. import exceptions, tools, constants
from . import mixins


class Fields(mixins.Parser):
    """Pass."""

    def _exists(self, item, source, desc):
        """Pass."""
        if item in source:
            msg = "{d} {i!r} already exists, duplicate??"
            msg = msg.format(d=desc, i=item)
            raise exceptions.ApiError(msg)

    def _generic(self):
        """Pass."""
        fields = {
            "all_data": {
                "name": "specific_data.data",
                "title": "All data subsets for generic adapter",
                "type": "array",
                "adapter_prefix": "specific_data",
            },
            "all": {
                "name": "specific_data",
                "title": "All data for generic adapter",
                "type": "array",
                "adapter_prefix": "specific_data",
            },
        }

        for field in self._raw["generic"]:
            field["adapter_prefix"] = "specific_data"
            field_name = tools.strip_left(
                obj=field["name"], fix="specific_data.data"
            ).strip(".")
            self._exists(field_name, fields, "Generic field")
            fields[field_name] = field

        return fields

    def _adapter(self, name, raw_fields):
        short_name = tools.strip_right(obj=name, fix="_adapter")

        prefix = "adapters_data.{adapter_name}"
        prefix = prefix.format(adapter_name=name)

        fields = {
            "all": {
                "name": prefix,
                "title": "All data for {} adapter".format(prefix),
                "type": "array",
                "adapter_prefix": prefix,
            },
            # this does not work any more as of 2.1.2 - unsure why
            # "raw": {
            #     "name": "{}.raw".format(prefix),
            #     "title": "All raw data for {} adapter".format(prefix),
            #     "type": "array",
            #     "adapter_prefix": prefix,
            # },
        }

        for field in raw_fields:
            field["adapter_prefix"] = prefix
            field_name = tools.strip_left(obj=field["name"], fix=prefix).strip(".")
            self._exists(field_name, fields, "Adapter {} field".format(short_name))
            fields[field_name] = field

        return short_name, fields

    def parse(self):
        """Pass."""
        ret = {}
        ret["generic"] = self._generic()

        for name, raw_fields in self._raw["specific"].items():
            short_name, fields = self._adapter(name=name, raw_fields=raw_fields)
            self._exists(short_name, ret, "Adapter {}".format(name))
            ret[short_name] = fields

        return ret


class Config(mixins.Parser):
    """Pass."""

    def parse(self, source, settings, adapter):
        """Pass."""
        new_config = {}

        for name, schema in settings.items():
            required = schema["required"]

            value = self._raw.get(name, None)

            has_value = name in self._raw
            has_default = "default" in schema

            req = "required" if required else "optional"
            msg = "Processing {req} setting {n!r} with value of {v!r}, schema: {ss}"
            msg = msg.format(req=req, n=name, v=value, ss=schema)
            self._log.debug(msg)

            if not has_value and not has_default:
                if not required:
                    continue

                raise exceptions.SettingMissing(
                    name=name, value=value, schema=schema, source=source,
                )

            if not has_value and has_default:
                value = schema["default"]

            new_config[name] = self.check_value(
                name=name, value=value, schema=schema, source=source, adapter=adapter
            )

        return new_config

    def check_value(self, name, value, schema, source, adapter=None):
        """Pass."""
        type_str = schema["type"]
        enum = schema.get("enum", [])

        if value == constants.SETTING_UNCHANGED:
            return value

        if enum and value not in enum:
            raise exceptions.SettingInvalidChoice(
                name=name, value=value, schema=schema, enum=enum, source=source
            )

        if type_str == "file":
            return self.check_adapter_file(
                name=name, value=value, schema=schema, source=source, adapter=adapter
            )
        elif type_str == "bool":
            return tools.coerce_bool(obj=value)
        elif type_str in ["number", "integer"]:
            return tools.coerce_int(obj=value)
        elif type_str == "array":
            if isinstance(value, tools.STR):
                value = [x.strip() for x in value.split(",")]
            if isinstance(value, tools.LIST) and all(
                [isinstance(x, tools.STR) for x in value]
            ):
                return value
        elif type_str == "string":
            if isinstance(value, tools.STR):
                return value
        else:
            raise exceptions.SettingUnknownType(
                name=name, value=value, schema=schema, type_str=type_str, source=source,
            )

        raise exceptions.SettingInvalidType(
            name=name, value=value, schema=schema, source=source, mustbe=type_str
        )

    def check_adapter_file(self, name, value, schema, source, adapter):
        """Pass."""
        is_str = isinstance(value, tools.STR)
        is_dict = isinstance(value, dict)
        is_path = isinstance(value, tools.pathlib.Path)

        if not any([is_dict, is_str, is_path]):
            raise exceptions.SettingInvalidType(
                name=name,
                value=value,
                schema=schema,
                mustbe="dict or str",
                source=source,
            )

        if is_str or is_path:
            value = {"filepath": format(value)}

        uuid = value.get("uuid", None)
        filename = value.get("filename", None)
        filepath = value.get("filepath", None)
        filecontent = value.get("filecontent", None)
        filecontent_type = value.get("filecontent_type", None)

        if uuid and filename:
            return {"uuid": uuid, "filename": filename}

        if filepath:
            uploaded = self._parent._parent.upload_file_path(
                field=name,
                adapter=adapter,
                path=filepath,
                content_type=filecontent_type,
            )

            return {"uuid": uploaded["uuid"], "filename": uploaded["filename"]}

        if filecontent and filename:
            uploaded = self._parent._parent.upload_file_str(
                field=name,
                adapter=adapter,
                name=filename,
                content=filecontent,
                content_type=filecontent_type,
            )
            return {"uuid": uploaded["uuid"], "filename": uploaded["filename"]}

        raise exceptions.SettingFileMissing(
            name=name, value=value, schema=schema, source=source
        )


class Adapters(mixins.Parser):
    """Pass."""

    def parse(self):
        """Pass.

        Returns:
            TYPE: Description

        """
        parsed = []

        for name, raw_adapters in self._raw.items():
            for raw in raw_adapters:
                adapter = self._adapter(name=name, raw=raw)
                parsed.append(adapter)

        return parsed

    def _adapter(self, name, raw):
        """Pass.

        Args:
            name (TYPE): Description
            raw (TYPE): Description

        Returns:
            TYPE: Description

        """
        parsed = {
            "name": tools.strip_right(obj=name, fix="_adapter"),
            "name_raw": name,
            "name_plugin": raw["unique_plugin_name"],
            "node_name": raw["node_name"],
            "node_id": raw["node_id"],
            "status_raw": raw["status"],
            "features": raw["supported_features"],
        }

        if parsed["status_raw"] == "success":
            parsed["status"] = True
        elif parsed["status_raw"] == "warning":
            parsed["status"] = False
        else:
            parsed["status"] = None

        cnx = self._cnx(raw=raw, parent=parsed)
        cnx_ok = [x for x in cnx if x["status"] is True]
        cnx_bad = [x for x in cnx if x["status"] is False]

        parsed["cnx"] = cnx
        parsed["cnx_ok"] = cnx_ok
        parsed["cnx_bad"] = cnx_bad
        parsed["cnx_settings"] = self._cnx_settings(raw=raw)
        parsed["cnx_count"] = len(cnx)
        parsed["cnx_count_ok"] = len(cnx_ok)
        parsed["cnx_count_bad"] = len(cnx_bad)
        parsed["settings"] = self._adapter_settings(raw=raw, base=False)
        parsed["adv_settings"] = self._adapter_settings(raw=raw, base=True)

        return parsed

    def _adapter_settings(self, raw, base=True):
        """Pass.

        Args:
            raw (TYPE): Description
            base (bool, optional): Description

        Returns:
            TYPE: Description

        """
        settings = {}

        for raw_name, raw_settings in raw["config"].items():
            is_base = raw_name == "AdapterBase"
            if ((is_base and base) or (not is_base and not base)) and not settings:
                schema = raw_settings["schema"]
                items = schema["items"]
                required = schema["required"]
                config = raw_settings["config"]

                for item in items:
                    setting_name = item["name"]
                    parsed_settings = {k: v for k, v in item.items()}
                    parsed_settings["required"] = setting_name in required
                    parsed_settings["value"] = config.get(setting_name, None)
                    settings[setting_name] = parsed_settings

        return settings

    def _cnx_settings(self, raw):
        """Pass.

        Args:
            raw (TYPE): Description

        Returns:
            TYPE: Description

        """
        settings = {}

        schema = raw["schema"]
        items = schema["items"]
        required = schema["required"]

        for item in items:
            setting_name = item["name"]
            settings[setting_name] = {k: v for k, v in item.items()}
            settings[setting_name]["required"] = setting_name in required

        return settings

    def _cnx(self, raw, parent):
        """Pass.

        Args:
            raw (TYPE): Description
            parent (TYPE): Description

        Returns:
            TYPE: Description

        """
        cnx = []

        cnx_settings = self._cnx_settings(raw=raw)

        for raw_cnx in raw["clients"]:
            raw_config = raw_cnx["client_config"]
            parsed_settings = {}

            for setting_name, setting_config in cnx_settings.items():
                value = raw_config.get(setting_name, None)

                if value == constants.SETTING_UNCHANGED:
                    value = "__HIDDEN__"

                if setting_name not in raw_config:
                    value = "__NOTSET__"

                parsed_settings[setting_name] = setting_config.copy()
                parsed_settings[setting_name]["value"] = value

            pcnx = {}
            pcnx["node_name"] = parent["node_name"]
            pcnx["node_id"] = parent["node_id"]
            pcnx["adapter_name"] = parent["name"]
            pcnx["adapter_name_raw"] = parent["name_raw"]
            pcnx["adapter_status"] = parent["status"]
            pcnx["config"] = parsed_settings
            pcnx["config_raw"] = raw_config
            pcnx["status_raw"] = raw_cnx["status"]
            pcnx["status"] = raw_cnx["status"] == "success"
            pcnx["id"] = raw_cnx["client_id"]
            pcnx["uuid"] = raw_cnx["uuid"]
            pcnx["date_fetched"] = raw_cnx["date_fetched"]
            pcnx["error"] = raw_cnx["error"]
            cnx.append(pcnx)

        return cnx
