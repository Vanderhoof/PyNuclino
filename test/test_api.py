import json
import os

from nuclino.api import Client
from nuclino.api import NuclinoError
from nuclino import objects
from pathlib import Path
from unittest import TestCase
from unittest import mock


def open_data_file(name):
    data_root = Path(os.path.abspath(__file__)).parent / 'test_data'
    with open(data_root / name) as f:
        return json.load(f)


class TestProcessResponse(TestCase):
    def setUp(self):
        self.client = Client('api_key')

    def test_error(self):
        response = mock.Mock()
        response.status_code = 400
        data = {'message': 'Error message'}
        response.json.return_value = data

        with self.assertRaises(NuclinoError) as exc:
            self.client._process_response(response)
            self.assertIn(str(response.status_code), str(exc))
            self.assertIn(data['message'], str(exc))

    @mock.patch('nuclino.api.Client.parse')
    def test_normal(self, parse):
        response = mock.Mock()
        response.status_code = 200
        data = {
            "status": "success",
            "data": {
                "id": "1034eebc-b96a-42b7-92ea-6795d6440fda"
            }
        }
        response.json.return_value = data

        self.client._process_response(response)
        parse.assert_called_with(data['data'])


class TestParse(TestCase):
    def setUp(self):
        self.client = Client('api_key')

    def test_delete_response(self):
        data = {"id": "1034eebc-b96a-42b7-92ea-6795d6440fda"}
        result = self.client.parse(data)
        self.assertEqual(result, data)
    
    def test_user(self):
        data = open_data_file('get_user.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, objects.User)

    def test_team(self):
        data = open_data_file('get_team.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, objects.Team)

    def test_teams(self):
        data = open_data_file('get_teams.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, list)
        for t in result:
            self.assertIsInstance(t, objects.Team)

    def test_workspace(self):
        data = open_data_file('get_workspace.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, objects.Workspace)

    def test_workspaces(self):
        data = open_data_file('get_workspaces.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, list)
        for t in result:
            self.assertIsInstance(t, objects.Workspace)

    def test_item(self):
        data = open_data_file('get_item.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, objects.Item)

    def test_cluster(self):
        data = open_data_file('get_collection.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, objects.Collection)

    def test_items(self):
        data = open_data_file('get_items.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, list)
        for t in result:
            self.assertIsInstance(t, (objects.Item, objects.Collection))

    def test_file(self):
        data = open_data_file('get_file.json')
        result = self.client.parse(data['data'])
        self.assertIsInstance(result, objects.File)
