# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi
from axonius_api_client import constants, exceptions, tools

from .. import utils
from . import test_api_users_devices
from . import meta


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    api = axonapi.Adapters(auth=auth)

    utils.check_apiobj(authobj=auth, apiobj=api)

    utils.check_apiobj_children(apiobj=api, cnx=axonapi.api.adapters.Cnx)
    return api


@pytest.fixture(scope="module")
def csv_adapter(apiobj):
    """Pass."""
    return apiobj.get_single(adapter="csv", node="master")


class TestConfig(object):
    """Pass."""

    def test_ignore(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1="test1", ignore="x")
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1="test1")

    def test_enum(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", required=True, enum=["test1"])
        )

        config = dict(test1="test1")
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1="test1")

    def test_enum_invalidchoice(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", required=True, enum=["test1"])
        )

        config = dict(test1="badwolf")
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.SettingInvalidChoice):
            parser.parse(adapter=csv_adapter, settings=fake_settings, source=source)

    def test_unchanged(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1=constants.SETTING_UNCHANGED)
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1=constants.SETTING_UNCHANGED)

    def test_string(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1="test1")
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1="test1")

    def test_number(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="number", required=True))

        config = dict(test1="2")

        source = apiobj._stringify(adapter=csv_adapter)
        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1=2)

    def test_integer(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="integer", required=True))

        config = dict(test1="2")
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1=2)

    def test_bool(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="bool", required=True))

        config = dict(test1=False)
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1=False)

    def test_optional_default(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", default="x", required=False)
        )

        config = dict()
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1="x")

    def test_optional_missing(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=False))

        config = dict()
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict()

    def test_required_default(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(
            test1=dict(name="test1", type="string", default="x", required=True)
        )

        config = dict()
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1="x")

    def test_required_missing(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict()
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.SettingMissing):
            parser.parse(adapter=csv_adapter, settings=fake_settings, source=source)

    def test_array(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="array", required=True))

        config = dict(test1=["test1"])
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1=["test1"])

    def test_array_comma(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="array", required=True))

        config = dict(test1="test1,test2,test3")
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1=["test1", "test2", "test3"])

    def test_array_invalidtype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="array", required=True))

        config = dict(test1=[True])
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.SettingInvalidType):
            parser.parse(adapter=csv_adapter, settings=fake_settings, source=source)

    def test_badtype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="string", required=True))

        config = dict(test1=True)
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.SettingInvalidType):
            parser.parse(adapter=csv_adapter, settings=fake_settings, source=source)

    def test_unknowntype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="badwolf", required=True))

        config = dict(test1="a")
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.SettingUnknownType):
            parser.parse(adapter=csv_adapter, settings=fake_settings, source=source)

    def test_file_badtype(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1=["X"])
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.SettingInvalidType):
            parser.parse(adapter=csv_adapter, settings=fake_settings, source=source)

    def test_file_missing(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1={})
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)

        with pytest.raises(exceptions.SettingFileMissing):
            parser.parse(adapter=csv_adapter, settings=fake_settings, source=source)

    def test_file_uuid(self, apiobj, csv_adapter):
        """Pass."""
        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1={"uuid": "x", "filename": "x", "ignore": "me"})
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1={"uuid": "x", "filename": "x"})

    def test_filename(self, apiobj, csv_adapter, monkeypatch):
        """Pass."""
        #
        def mock_upload_file(**kwargs):
            """Pass."""
            return {"uuid": "x", "filename": "badwolf"}

        monkeypatch.setattr(apiobj, "_upload_file", mock_upload_file)

        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        config = dict(test1={"filename": "x", "filecontent": "x"})
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(test1={"uuid": "x", "filename": "badwolf"})

    def test_filepath(self, apiobj, csv_adapter, monkeypatch, tmp_path):
        """Pass."""
        #
        def mock_upload_file(**kwargs):
            """Pass."""
            return {"uuid": "x", "filename": meta.csv.CSV_FILENAME}

        monkeypatch.setattr(apiobj, "_upload_file", mock_upload_file)

        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        test_path = tmp_path / meta.csv.CSV_FILENAME
        test_path.write_text(meta.csv.CSV_FILECONTENT_STR)

        config = dict(test1={"filepath": test_path})
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(
            test1={"uuid": "x", "filename": meta.csv.CSV_FILENAME}
        )

    def test_filepath_str(self, apiobj, csv_adapter, monkeypatch, tmp_path):
        """Pass."""
        #
        def mock_upload_file(**kwargs):
            """Pass."""
            return {"uuid": "x", "filename": meta.csv.CSV_FILENAME}

        monkeypatch.setattr(apiobj, "_upload_file", mock_upload_file)

        fake_settings = dict(test1=dict(name="test1", type="file", required=True))

        test_path = tmp_path / meta.csv.CSV_FILENAME
        test_path.write_text(meta.csv.CSV_FILECONTENT_STR)

        config = dict(test1=format(test_path))
        source = apiobj._stringify(adapter=csv_adapter)

        parser = axonapi.api.parsers.Config(raw=config, parent=apiobj.cnx)
        parsed_config = parser.parse(
            adapter=csv_adapter, settings=fake_settings, source=source
        )

        assert parsed_config == dict(
            test1={"uuid": "x", "filename": meta.csv.CSV_FILENAME}
        )


class TestAdapters(object):
    """Pass."""

    def test_adapters(self, apiobj):
        """Pass."""
        raw = apiobj._get()
        parser = axonapi.api.parsers.Adapters(raw=raw, parent=apiobj)
        adapters = parser.parse()
        assert isinstance(adapters, tools.LIST)
        for adapter in adapters:
            self.validate_adapter(adapter)

    def validate_cnx(self, aname, aname_raw, astatus, anid, anname, cnx):
        """Pass."""
        assert isinstance(cnx, dict)
        adapter_name = cnx.pop("adapter_name")
        adapter_name_raw = cnx.pop("adapter_name_raw")
        adapter_status = cnx.pop("adapter_status")
        config = cnx.pop("config")
        config_raw = cnx.pop("config_raw")
        date_fetched = cnx.pop("date_fetched")
        error = cnx.pop("error")
        cid = cnx.pop("id")
        node_id = cnx.pop("node_id")
        node_name = cnx.pop("node_name")
        status = cnx.pop("status")
        status_raw = cnx.pop("status_raw")
        uuid = cnx.pop("uuid")

        assert adapter_name == aname
        assert adapter_name_raw == aname_raw
        assert adapter_status == astatus
        assert isinstance(config, dict) and config
        assert isinstance(config_raw, dict) and config_raw
        assert isinstance(date_fetched, tools.STR)
        assert isinstance(error, tools.STR) or error is None
        assert isinstance(cid, tools.STR)
        assert node_id == anid
        assert node_name == anname
        assert isinstance(status, bool)
        assert isinstance(status_raw, tools.STR)
        assert isinstance(uuid, tools.STR)

        if status is False:
            assert astatus is False

        if status is True:
            assert astatus in [True, False]

        assert not cnx

    def validate_settings(self, settings, check_value):
        """Pass."""
        for name, item in settings.items():
            item_name = item.pop("name")
            item_type = item.pop("type")
            item_title = item.pop("title")
            item_format = item.pop("format", "")
            item_description = item.pop("description", "")
            item_enum = item.pop("enum", [])
            item_default = item.pop("default", "")
            item_items = item.pop("items", {})
            item_required = item.pop("required")

            if check_value:
                item_value = item.pop("value")
                assert isinstance(item_value, tools.SIMPLE) or item_value in [None, []]

            assert isinstance(item_name, tools.STR) and item_name
            assert isinstance(item_type, tools.STR) and item_type
            assert isinstance(item_title, tools.STR) and item_title
            assert isinstance(item_items, dict)
            assert isinstance(item_default, tools.SIMPLE) or item_default in [None, []]
            assert isinstance(item_enum, tools.LIST)
            for x in item_enum:
                assert isinstance(x, tools.STR)
            assert isinstance(item_format, tools.STR)
            assert isinstance(item_description, tools.STR)
            assert isinstance(item_required, bool)
            assert item_type in ["number", "integer", "string", "bool", "array", "file"]
            assert not item

    def validate_adapter(self, adapter):
        """Pass."""
        assert isinstance(adapter, dict)

        adv_settings = adapter.pop("adv_settings")
        cnx = adapter.pop("cnx")
        cnx_bad = adapter.pop("cnx_bad")
        cnx_count = adapter.pop("cnx_count")
        cnx_count_bad = adapter.pop("cnx_count_bad")
        cnx_count_ok = adapter.pop("cnx_count_ok")
        cnx_ok = adapter.pop("cnx_ok")
        cnx_settings = adapter.pop("cnx_settings")
        features = adapter.pop("features")
        name = adapter.pop("name")
        name_plugin = adapter.pop("name_plugin")
        name_raw = adapter.pop("name_raw")
        node_id = adapter.pop("node_id")
        node_name = adapter.pop("node_name")
        settings = adapter.pop("settings")
        status = adapter.pop("status")
        status_raw = adapter.pop("status_raw")

        assert isinstance(name, tools.STR)
        assert isinstance(name_raw, tools.STR)
        assert isinstance(name_plugin, tools.STR)
        assert isinstance(node_name, tools.STR)
        assert isinstance(node_id, tools.STR)
        assert isinstance(status_raw, tools.STR)
        assert isinstance(features, tools.LIST)
        for x in features:
            assert isinstance(x, tools.STR)
        assert isinstance(cnx_count, tools.INT)
        assert isinstance(cnx_count_ok, tools.INT)
        assert isinstance(cnx_count_bad, tools.INT)
        assert isinstance(status, bool) or status is None
        assert isinstance(cnx_settings, dict)
        assert isinstance(settings, dict)
        assert isinstance(adv_settings, dict)

        self.validate_settings(settings, True)
        self.validate_settings(adv_settings, True)
        self.validate_settings(cnx_settings, False)

        for cnxs in [cnx, cnx_ok, cnx_bad]:
            assert isinstance(cnxs, tools.LIST)
            for connection in [x for x in cnxs if x]:
                self.validate_cnx(
                    aname=name,
                    aname_raw=name_raw,
                    anid=node_id,
                    anname=node_name,
                    astatus=status,
                    cnx=connection,
                )

        assert not adapter


@pytest.mark.parametrize(
    "apicls", [(axonapi.api.Users), (axonapi.Devices)], scope="class"
)
class TestFields(test_api_users_devices.Base):
    """Pass."""

    def test_fields(self, apiobj):
        """Pass."""
        raw = apiobj.fields._get()
        parser = axonapi.api.parsers.Fields(raw=raw, parent=apiobj)
        fields = parser.parse()

        with pytest.raises(exceptions.ApiError):
            parser._exists("generic", fields, "dumb test")

        assert isinstance(fields, dict)

        for aname, afields in fields.items():
            assert not aname.endswith("_adapter")
            assert isinstance(afields, dict)

            if aname == "generic":
                gall_data = afields.pop("all_data")
                assert isinstance(gall_data, dict)

                gall_data_name = gall_data.pop("name")
                gall_data_type = gall_data.pop("type")
                gall_data_prefix = gall_data.pop("adapter_prefix")
                gall_data_title = gall_data.pop("title")

                assert not gall_data, list(gall_data)
                assert gall_data_name == "specific_data.data"
                assert gall_data_type == "array"
                assert gall_data_prefix == "specific_data"
                assert gall_data_title == "All data subsets for generic adapter"

                gall = afields.pop("all")
                assert isinstance(gall, dict)

                gall_name = gall.pop("name")
                gall_type = gall.pop("type")
                gall_prefix = gall.pop("adapter_prefix")
                gall_title = gall.pop("title")

                assert not gall, list(gall)
                assert gall_name == "specific_data"
                assert gall_type == "array"
                assert gall_prefix == "specific_data"
                assert gall_title == "All data for generic adapter"

            else:
                # no longer works as of 2.1.2 - unsure why
                # graw = afields.pop("raw")
                # assert isinstance(graw, dict)
                # assert graw["name"].endswith(".raw")

                gall = afields.pop("all")
                assert isinstance(gall, dict)
                assert gall["name"] == "adapters_data.{}_adapter".format(aname)

            for fname, finfo in afields.items():
                self.val_field(fname, finfo, aname)

    def val_field(self, fname, finfo, aname):
        """Pass."""
        assert isinstance(finfo, dict)

        # common
        name = finfo.pop("name")
        type = finfo.pop("type")
        prefix = finfo.pop("adapter_prefix")
        title = finfo.pop("title")

        assert isinstance(name, tools.STR) and name
        assert isinstance(title, tools.STR) and title
        assert isinstance(prefix, tools.STR) and prefix
        assert isinstance(type, tools.STR) and type

        # uncommon
        items = finfo.pop("items", {})
        sort = finfo.pop("sort", False)
        unique = finfo.pop("unique", False)
        branched = finfo.pop("branched", False)
        enums = finfo.pop("enum", [])
        description = finfo.pop("description", "")
        dynamic = finfo.pop("dynamic", False)
        format = finfo.pop("format", "")

        assert isinstance(items, dict)
        assert isinstance(sort, bool)
        assert isinstance(unique, bool)
        assert isinstance(branched, bool)
        assert isinstance(enums, tools.LIST)
        assert isinstance(description, tools.STR)
        assert isinstance(dynamic, bool)
        assert isinstance(format, tools.STR)

        assert not finfo, list(finfo)

        assert type in meta.fields.FIELD_TYPES, type

        if name not in ["labels", "adapters", "internal_axon_id"]:
            if aname == "generic":
                assert name.startswith("specific_data")
            else:
                assert name.startswith(prefix)

        for enum in enums:
            assert isinstance(enum, tools.STR) or tools.is_int(enum)

        if format:
            assert format in meta.fields.FIELD_FORMATS, format

        self.val_items(aname="{}:{}".format(aname, fname), items=items)

    def val_items(self, aname, items):
        """Pass."""
        assert isinstance(items, dict)

        if items:
            # common
            type = items.pop("type")

            assert isinstance(type, tools.STR) and type
            assert type in meta.fields.FIELD_TYPES, type

            # uncommon
            enums = items.pop("enum", [])
            fformat = items.pop("format", "")
            iitems = items.pop("items", [])
            name = items.pop("name", "")
            title = items.pop("title", "")
            description = items.pop("description", "")
            branched = items.pop("branched", False)
            dynamic = items.pop("dynamic", False)
            source = items.pop("source", {})
            assert isinstance(source, dict)

            if source:
                source_key = source.pop("key")
                assert isinstance(source_key, tools.STR)

                source_options = source.pop("options")
                assert isinstance(source_options, dict)

                options_allow = source_options.pop("allow-custom-option")
                assert isinstance(options_allow, bool)

                assert not source, source
                assert not source_options, source_options

            if fformat:
                assert fformat in meta.fields.SCHEMA_FIELD_FORMATS, fformat

            assert isinstance(enums, tools.LIST)
            assert isinstance(iitems, tools.LIST) or isinstance(iitems, dict)
            assert isinstance(fformat, tools.STR)
            assert isinstance(name, tools.STR)
            assert isinstance(title, tools.STR)
            assert isinstance(description, tools.STR)
            assert isinstance(branched, bool)
            assert isinstance(dynamic, bool)

            assert not items, list(items)

            for enum in enums:
                assert isinstance(enum, tools.STR) or tools.is_int(enum)

            if isinstance(iitems, dict):
                self.val_items(aname=aname, items=iitems)
            else:
                for iitem in iitems:
                    self.val_items(aname=aname, items=iitem)
