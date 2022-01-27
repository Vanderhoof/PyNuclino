import requests

from typing import List
from typing import Optional
from typing import Union

from ratelimit import limits
from .utils import sleep_and_retry

from .objects import Cluster
from .objects import File
from .objects import Item
from .objects import NuclinoObject
from .objects import Team
from .objects import Workspace
from .objects import get_loader


BASE_URL = 'https://api.nuclino.com/v0'


class NuclinoError(Exception):
    pass


def join_url(base_url, path):
    return '/'.join(part.strip('/') for part in [base_url, path])


class Client:
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = BASE_URL,
        requests_per_minute: int = 140
    ):
        self.check_limit = sleep_and_retry()(
            limits(requests_per_minute, period=60)(lambda: None)
        )
        self.session = requests.Session()
        self.session.headers['Authorization'] = api_key
        self.timer = None
        self.base_url = base_url

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        self.session.close()

    def _process_response(self, response: requests.models.Response) -> Union[List, NuclinoObject]:
        content = response.json()
        if response.status_code != 200:
            message = content.get('message', '')
            raise NuclinoError(f'{response.status_code}: {message}')
        else:
            data = content['data']
            return self.parse(data)

    def parse(self, source: dict) -> Union[List, NuclinoObject, dict]:
        if 'object' not in source:
            return source
        func = get_loader(source['object'])
        result = func(source, self)
        if isinstance(result, NuclinoObject):
            return result
        elif isinstance(result, list):
            return [self.parse(li) for li in result]

    def get(self, path: str, params: dict = {}) -> Union[List, NuclinoObject]:
        self.check_limit()
        response = self.session.get(join_url(self.base_url, path), params=params)
        return self._process_response(response)

    def delete(self, path: str) -> dict:
        self.check_limit()
        response = self.session.delete(join_url(self.base_url, path))
        return self._process_response(response)

    def post(self, path: str, data: dict) -> dict:
        headers = {'Content-Type': 'application/json'}
        self.check_limit()
        response = self.session.post(
            join_url(self.base_url, path),
            json=data,
            headers=headers
        )
        return self._process_response(response)

    def put(self, path: str, data: dict) -> dict:
        headers = {'Content-Type': 'application/json'}
        self.check_limit()
        response = self.session.put(
            join_url(self.base_url, path),
            json=data,
            headers=headers
        )
        return self._process_response(response)


class Nuclino(Client):
    def get_teams(
        self,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> List[Team]:
        path = '/teams'
        params = {}
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        return self.get(path, params)

    def get_team(self, team_id: str):
        path = f'/teams/{team_id}'
        return self.get(path)

    def get_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> List[Workspace]:
        path = '/workspaces'
        params = {}
        if team_id is not None:
            params['teamId'] = team_id
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        return self.get(path, params)

    def get_workspace(self, workspace_id: str) -> Workspace:
        path = f'/workspaces/{workspace_id}'
        return self.get(path)

    def get_items(
        self,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Union[Item, Cluster]]:
        path = '/items'
        params = {}
        if team_id is not None:
            params['teamId'] = team_id
        if workspace_id is not None:
            params['workspaceId'] = workspace_id
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        if search is not None:
            params['search'] = search
        return self.get(path, params)

    def get_item(self, item_id: str) -> Union[Item, Cluster]:
        path = f'/items/{item_id}'
        return self.get(path)

    def get_cluster(self, cluster_id: str) -> Union[Item, Cluster]:
        return self.get_item(cluster_id)

    def create_item(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        object: Optional[str] = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Cluster]:
        path = f'/items'
        data = {'object': object}
        if workspace_id is not None:
            data['workspaceId'] = workspace_id
        if parent_id is not None:
            data['parentId'] = parent_id
        if title is not None:
            data['title'] = title
        if content is not None:
            data['content'] = content
        if index is not None:
            data['index'] = str(index)
        return self.post(path, data)

    def create_cluster(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        title: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Cluster]:
        return self.create_item(
            workspace_id=workspace_id,
            parent_id=parent_id,
            object='cluster',
            title=title,
            content=None,
            index=index
        )

    def update_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Union[Item, Cluster]:
        path = f'/items/{item_id}'
        data = {}
        if title is not None:
            data['title'] = title
        if content is not None:
            data['content'] = content
        return self.put(path, data=data)

    def update_cluster(
        self,
        cluster_id: str,
        title: Optional[str] = None
    ) -> Union[Item, Cluster]:
        return self.update_item(cluster_id, title=title, content=None)

    def delete_item(self, item_id: str) -> dict:
        path = f'/items/{item_id}'
        return self.delete(path)

    def delete_cluster(self, cluster_id: str) -> dict:
        return self.delete_item(cluster_id)

    def get_file(self, file_id: str) -> File:
        path = f'/files/{file_id}'
        return self.get(path)
