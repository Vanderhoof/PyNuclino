'''
These tests call live API and require API_KEY env var to be set.
Beware of rate limiting while running these tests.
At the time of writing there's a limit of 150 requests per minute.
This test suite runs 34 requests.
'''

import os

from nuclino import objects
from nuclino.api import Nuclino
from unittest import TestCase


API_KEY = os.environ['API_KEY']


class TestCaseWithKey(TestCase):
    def setUp(self):
        self.client = Nuclino(API_KEY)

    def tearDown(self):
        self.client.close()


class TestTeams(TestCaseWithKey):
    def test_normal(self):
        result = self.client.get_teams()  # 1req
        for t in result:
            self.assertIsInstance(t, objects.Team)

    def test_limit(self):
        result = self.client.get_teams(limit=1)  # 1req
        self.assertEqual(len(result), 1)

    def test_after(self):
        teams = self.client.get_teams()  # 1req
        team_id = teams[0].id
        result = self.client.get_teams(after=team_id)  # 1req
        if result:
            self.assertFalse(result[0].id == team_id)

    def test_team(self):
        teams = self.client.get_teams()  # 1req
        team_id = teams[0].id
        result = self.client.get_team(team_id)
        self.assertIsInstance(result, objects.Team)


class TestWorkspaces(TestCaseWithKey):
    def test_normal(self):
        result = self.client.get_workspaces()  # 1req
        for t in result:
            self.assertIsInstance(t, objects.Workspace)

    def test_limit(self):
        result = self.client.get_workspaces(limit=1)  # 1req
        self.assertEqual(len(result), 1)

    def test_after(self):
        workspaces = self.client.get_workspaces()  # 1req
        workspace_id = workspaces[0].id
        result = self.client.get_workspaces(after=workspace_id)  # 1req
        if result:
            self.assertFalse(result[0].id == workspace_id)

    def test_workspace(self):
        workspaces = self.client.get_workspaces()  # 1req
        workspace_id = workspaces[0].id
        result = self.client.get_workspace(workspace_id)
        self.assertIsInstance(result, objects.Workspace)

    def test_team_id(self):
        teams = self.client.get_teams()  # 1req
        team_id = teams[0].id
        result = self.client.get_workspaces(team_id=team_id)  # 1req
        self.assertEqual(result[0].team_id, team_id)


class TestItems(TestCaseWithKey):
    def test_by_workspace(self):
        workspaces = self.client.get_workspaces()
        workspace_id = workspaces[0].id
        result = self.client.get_items(workspace_id=workspace_id)  # 1req
        for i in result:
            self.assertIsInstance(i, (objects.Item, objects.Cluster))

    def test_by_team(self):
        teams = self.client.get_teams()
        team_id = teams[0].id
        result = self.client.get_items(team_id=team_id)  # 1req
        for i in result:
            self.assertIsInstance(i, (objects.Item, objects.Cluster))

    def test_limit(self):
        workspaces = self.client.get_workspaces()
        workspace_id = workspaces[0].id
        result = self.client.get_items(workspace_id=workspace_id, limit=1)  # 1req
        self.assertEqual(len(result), 1)

    def test_after(self):
        workspaces = self.client.get_workspaces()
        workspace_id = workspaces[0].id

        items = self.client.get_items(workspace_id=workspace_id)  # 1req
        item_id = items[0].id
        result = self.client.get_items(workspace_id=workspace_id,
                                       after=item_id)  # 1req
        if result:
            self.assertFalse(result[0].id == item_id)

    def test_search(self):
        teams = self.client.get_teams()
        team_id = teams[0].id
        items = self.client.get_items(team_id=team_id)  # 1req
        filtered = self.client.get_items(team_id=team_id,
                                         search='welcome')  # 1req
        self.assertNotEqual(len(items), len(filtered))

    def test_item(self):
        teams = self.client.get_teams()
        team_id = teams[0].id
        items = self.client.get_items(team_id=team_id)  # 1req
        result = self.client.get_item(items[0].id)
        self.assertIsInstance(result, (objects.Item, objects.Cluster))


class TestModifyItems(TestCaseWithKey):
    def test_create_item(self):
        workspaces = self.client.get_workspaces()  # 1req
        workspace_id = workspaces[0].id
        item = self.client.create_item(
            workspace_id=workspace_id,
            object='item',
            title='Test Title',
            content='Test content\n'
        )  # 1req
        self.assertIsInstance(item, objects.Item)
        item.delete()  # 1req

    def test_create_child(self):
        workspaces = self.client.get_workspaces()  # 1req
        workspace_id = workspaces[0].id
        cluster = self.client.create_item(
            workspace_id=workspace_id,
            object='cluster',
            title='Test Cluster',
        )  # 1req
        self.assertIsInstance(cluster, objects.Cluster)

        item = self.client.create_item(
            parent_id=cluster.id,
            object='item',
            title='Test Title',
            content='Test content\n'
        )  # 1req
        self.assertIsInstance(item, objects.Item)
        item.delete()  # 1req
        cluster.delete()  # 1req

    def test_update_item(self):
        workspaces = self.client.get_workspaces()  # 1req
        workspace_id = workspaces[0].id
        item = self.client.create_item(
            workspace_id=workspace_id,
            object='item',
            title='Test Title',
            content='Test content\n'
        )  # 1req
        new_title = 'New Title'
        new_content = 'New Content\n'
        updated_item = self.client.update_item(item.id,
                                               title=new_title,
                                               content=new_content)  # 1req
        self.assertIsInstance(updated_item, objects.Item)
        self.assertEqual(updated_item.title, new_title)
        self.assertEqual(updated_item.content, new_content)
        item.delete()  # 1req

    def test_delete_item(self):
        workspaces = self.client.get_workspaces()  # 1req
        workspace_id = workspaces[0].id
        item = self.client.create_item(
            workspace_id=workspace_id,
            object='item',
            title='Test Title',
            content='Test content\n'
        )  # 1req
        item_id = item.id
        result = self.client.delete_item(item_id)
        self.assertEqual(result['id'], item_id)
