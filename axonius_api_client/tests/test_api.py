# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import axonius_api_client


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize("creds", ["creds_user", "creds_key"], indirect=True)
class TestApiUsers(object):
    """Test axonius_api_client.api.ApiUsers."""

    @pytest.fixture(scope="session")
    def api_client(self, api_url, creds):
        """Get an API client."""
        auth_cls = creds["cls"]
        creds = {k: v for k, v in creds.items() if k != "cls"}
        if not any(list(creds.values())):
            pytest.skip("No credentials provided for {}: {}".format(auth_cls, creds))
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = auth_cls(http_client=http_client, **creds)
        api_client = axonius_api_client.api.ApiUsers(auth=auth)
        return api_client

    def test_str_repr(self, api_client):
        """Test str/repr has URL."""
        assert "auth" in format(api_client)
        assert "auth" in repr(api_client)

    def test_get_fields(self, api_client):
        """Test devices/fields API call."""
        fields = api_client.get_fields()
        assert isinstance(fields, dict)
        assert "specific" in fields
        assert "generic" in fields
        assert "schema" in fields

    def test__get_no_query_no_fields(self, api_client):
        """Test private get method without query or fields."""
        rows = api_client._get(query=None, fields=None, row_start=0, page_size=1)
        assert "assets" in rows
        for row in rows["assets"]:
            assert "adapters" in row
            assert "specific_data" in row

    @pytest.mark.parametrize(
        "fields",
        [
            ["specific_data.data.username", "specific_data.data.id"],
            "specific_data.data.username,specific_data.data.id",
        ],
    )
    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test__get_queries_fields(self, api_client, query, fields):
        """Test private get method with queries and fields."""
        rows = api_client._get(query=query, fields=fields, row_start=0, page_size=1)
        assert "assets" in rows
        for row in rows["assets"]:
            assert "adapters" in row
            assert "internal_axon_id" in row
            assert "specific_data.data.username" in row
            assert "specific_data.data.id" in row

    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test_get_no_fields(self, api_client, query):
        """Test private get method with default fields."""
        for dvc in api_client.get(query=query, page_size=1, max_rows=2):
            assert "specific_data.data.username" in dvc

    def test_get_by_id_valid(self, api_client):
        """Test get_by_id with a valid row id."""
        rows = api_client._get(page_size=1)
        for row in rows["assets"]:
            full_row = api_client.get_by_id(id=row["internal_axon_id"])
            assert "generic" in full_row
            assert "specific" in full_row

    def test_get_by_id_invalid(self, api_client):
        """Test get_by_id with an invalid row id."""
        with pytest.raises(axonius_api_client.exceptions.ObjectNotFound):
            api_client.get_by_id(id="this_wont_work_yo")

    def test_get_count(self, api_client):
        """Test devices/count API call."""
        response = api_client.get_count()
        assert isinstance(response, int)

    def test_get_count_query(self, api_client):
        """Test devices/count API call with query (unable to assume greater than 0)."""
        response = api_client.get_count(
            query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
        )
        assert isinstance(response, int)

    def test_get_count_query_0(self, api_client):
        """Test devices/count API call with query that should return 0."""
        response = api_client.get_count(
            query='(specific_data.data.id == ({"$exists":false,"$eq": "dsaf"}))'
        )
        assert response == 0

    def test__get_saved_query(self, api_client):
        """Test private get_saved_query."""
        rows = api_client._get_saved_query()
        assert isinstance(rows, dict)
        assert "assets" in rows
        assert "page" in rows

    def test_get_saved_query_by_name_invalid(self, api_client):
        """Test get_saved_query_by_name."""
        with pytest.raises(axonius_api_client.exceptions.ObjectNotFound):
            api_client.get_saved_query_by_name(name="this_wont_exist_yo", regex=False)

    @pytest.fixture
    def test_create_saved_query_badwolf123(self, api_client):
        """Test create_saved_query."""
        name = "badwolf 123"
        response = api_client.create_saved_query(
            name=name, query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
        )
        assert isinstance(response, str)
        return name, response

    @pytest.fixture
    def test_create_saved_query_badwolf456(self, api_client):
        """Test create_saved_query."""
        name = "badwolf 456"
        response = api_client.create_saved_query(
            name=name,
            query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))',
            sort_field="id",
        )
        assert isinstance(response, str)
        return name, response

    def test_get_saved_query_by_name_valid(
        self, api_client, test_create_saved_query_badwolf123
    ):
        """Test get_saved_query_by_name."""
        name, id = test_create_saved_query_badwolf123
        rows = api_client.get_saved_query_by_name(name=name, regex=True)
        assert isinstance(rows, list)
        assert len(rows) > 0
        for row in rows:
            assert "name" in row
            assert "uuid" in row

    @pytest.mark.parametrize("query", [None, 'name == regex("badwolf", "i")'])
    def test_get_saved_query(
        self, api_client, query, test_create_saved_query_badwolf123
    ):
        """Test get_saved_query."""
        rows = list(api_client.get_saved_query(query=query))
        assert isinstance(rows, list)
        assert len(rows) > 0
        for row in rows:
            assert "name" in row
            assert "uuid" in row

    def test_delete_saved_query_by_name(
        self, api_client, test_create_saved_query_badwolf123
    ):
        """Test delete_saved_query_by_name."""
        name, id = test_create_saved_query_badwolf123
        rows = api_client.delete_saved_query_by_name(name=name)
        assert not rows

    def test__delete_saved_query(self, api_client, test_create_saved_query_badwolf456):
        """Test private _delete_saved_query."""
        name, id = test_create_saved_query_badwolf456
        rows = api_client._delete_saved_query(ids=[id])
        assert not rows


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize("creds", ["creds_user", "creds_key"], indirect=True)
class TestApiDevices(object):
    """Test axonius_api_client.api.ApiDevices."""

    @pytest.fixture(scope="session")
    def api_client(self, api_url, creds):
        """Get an API client."""
        auth_cls = creds["cls"]
        creds = {k: v for k, v in creds.items() if k != "cls"}
        if not any(list(creds.values())):
            pytest.skip("No credentials provided for {}: {}".format(auth_cls, creds))
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = auth_cls(http_client=http_client, **creds)
        api_client = axonius_api_client.api.ApiDevices(auth=auth)
        return api_client

    def test__request_invalid(self, api_client):
        """Test private _request method throws ResponseError."""
        with pytest.raises(axonius_api_client.exceptions.ResponseError):
            api_client._request(route="invalid_route")

    def test_str_repr(self, api_client):
        """Test str/repr has URL."""
        assert "auth" in format(api_client)
        assert "auth" in repr(api_client)

    def test_get_fields(self, api_client):
        """Test devices/fields API call."""
        fields = api_client.get_fields()
        assert isinstance(fields, dict)
        assert "specific" in fields
        assert "generic" in fields
        assert "schema" in fields

    def test__get_no_query_no_fields(self, api_client):
        """Test private get method without query or fields."""
        rows = api_client._get(query=None, fields=None, row_start=0, page_size=1)
        assert "assets" in rows
        for row in rows["assets"]:
            assert "adapters" in row
            assert "specific_data" in row

    @pytest.mark.parametrize(
        "fields",
        [
            [
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
            ],
            "specific_data.data.hostname,specific_data.data.network_interfaces.ips",
        ],
    )
    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test__get_queries_fields(self, api_client, query, fields):
        """Test private get method with queries and fields."""
        rows = api_client._get(query=query, fields=fields, row_start=0, page_size=1)
        assert "assets" in rows
        for row in rows["assets"]:
            assert "adapters" in row
            assert "internal_axon_id" in row
            assert "specific_data.data.hostname" in row
            assert "specific_data.data.network_interfaces.ips" in row

    @pytest.mark.parametrize(
        "query", [None, '(specific_data.data.id == ({"$exists":true,"$ne": ""}))']
    )
    def test_get_no_fields(self, api_client, query):
        """Test private get method with default fields."""
        for dvc in api_client.get(query=query, page_size=1, max_rows=2):
            assert "specific_data.data.hostname" in dvc
            assert "specific_data.data.network_interfaces.ips" in dvc
            # FUTURE: add cmd line option for adapter fields
            # --adapter_fields cisco:hostname,network_interfaces.ips

    def test_get_by_id_valid(self, api_client):
        """Test get_by_id with a valid row id."""
        rows = api_client._get(page_size=1)
        for row in rows["assets"]:
            full_row = api_client.get_by_id(id=row["internal_axon_id"])
            assert "generic" in full_row
            assert "specific" in full_row

    def test_get_by_id_invalid(self, api_client):
        """Test get_by_id with an invalid row id."""
        with pytest.raises(axonius_api_client.exceptions.ObjectNotFound):
            api_client.get_by_id(id="this_wont_work_yo")

    def test_get_count(self, api_client):
        """Test devices/count API call."""
        response = api_client.get_count()
        assert isinstance(response, int)

    def test_get_count_query(self, api_client):
        """Test devices/count API call with query (unable to assume greater than 0)."""
        response = api_client.get_count(
            query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
        )
        assert isinstance(response, int)

    def test_get_count_query_0(self, api_client):
        """Test devices/count API call with query that should return 0."""
        response = api_client.get_count(
            query='(specific_data.data.id == ({"$exists":false,"$eq": "dsaf"}))'
        )
        assert response == 0

    def test__get_saved_query(self, api_client):
        """Test private get_saved_query."""
        rows = api_client._get_saved_query()
        assert isinstance(rows, dict)
        assert "assets" in rows
        assert "page" in rows

    def test_get_saved_query_by_name_invalid(self, api_client):
        """Test get_saved_query_by_name."""
        with pytest.raises(axonius_api_client.exceptions.ObjectNotFound):
            api_client.get_saved_query_by_name(name="this_wont_exist_yo", regex=False)

    @pytest.fixture
    def test_create_saved_query_badwolf123(self, api_client):
        """Test create_saved_query."""
        name = "badwolf 123"
        response = api_client.create_saved_query(
            name=name, query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))'
        )
        assert isinstance(response, str)
        return name, response

    @pytest.fixture
    def test_create_saved_query_badwolf456(self, api_client):
        """Test create_saved_query."""
        name = "badwolf 456"
        response = api_client.create_saved_query(
            name=name,
            query='(specific_data.data.id == ({"$exists":true,"$ne": ""}))',
            sort_field="id",
        )
        assert isinstance(response, str)
        return name, response

    def test_get_saved_query_by_name_valid(
        self, api_client, test_create_saved_query_badwolf123
    ):
        """Test get_saved_query_by_name."""
        name, id = test_create_saved_query_badwolf123
        rows = api_client.get_saved_query_by_name(name=name, regex=True)
        assert isinstance(rows, list)
        assert len(rows) > 0
        for row in rows:
            assert "name" in row
            assert "uuid" in row

    @pytest.mark.parametrize("query", [None, 'name == regex("badwolf", "i")'])
    def test_get_saved_query(
        self, api_client, query, test_create_saved_query_badwolf123
    ):
        """Test get_saved_query."""
        rows = list(api_client.get_saved_query(query=query))
        assert isinstance(rows, list)
        assert len(rows) > 0
        for row in rows:
            assert "name" in row
            assert "uuid" in row

    def test_delete_saved_query_by_name(
        self, api_client, test_create_saved_query_badwolf123
    ):
        """Test delete_saved_query_by_name."""
        name, id = test_create_saved_query_badwolf123
        rows = api_client.delete_saved_query_by_name(name=name)
        assert not rows

    def test__delete_saved_query(self, api_client, test_create_saved_query_badwolf456):
        """Test private _delete_saved_query."""
        name, id = test_create_saved_query_badwolf456
        rows = api_client._delete_saved_query(ids=[id])
        assert not rows
