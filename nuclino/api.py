import requests

from typing import List
from typing import Optional
from typing import Union

from ratelimit import limits
from .utils import sleep_and_retry

from .objects import NuclinoObject
from .objects import get_loader


BASE_URL = 'https://api.nuclino.com/v0'


class NuclinoError(Exception):
    pass


def join_url(base_url, path):
    return '/'.join(part.strip('/') for part in [base_url, path])


class Client:
    '''
    Base class for Nuclino API client. May be used as a context processor.
    '''

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = BASE_URL,
        requests_per_minute: int = 140
    ):
        '''
        :param api_key:       your Nuclino API key.
        :param base_url:      base url to send API requests.
        :requests_per_minute: max requests per minute. If limit exceeded, client will wait
                              for some time before processing the next request.
        '''
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

    def _process_response(
        self,
        response: requests.models.Response
    ) -> Union[List, NuclinoObject, dict]:
        '''
        General method that processes API responses. Raises error on HTTP
        errors, sends results to parser on 200 ok.

        :param response: response object, received after calling API.
        '''
        content = response.json()
        if response.status_code != 200:
            message = content.get('message', '')
            raise NuclinoError(f'{response.status_code}: {message}')
        else:
            data = content['data']
            return self.parse(data)

    def parse(self, source: dict) -> Union[List, NuclinoObject, dict]:
        '''
        Parse successful response dictionary. This method will determine the
        type of object, that was returned, and construct corresponding
        NuclinoObject as the return result.

        :param source: the "data" dictionary from Nuclino API response.
        :returns:      corresponsing NuclinoObject constructed from `source`.
        '''

        if 'object' not in source:
            return source
        func = get_loader(source['object'])
        result = func(source, self)
        if isinstance(result, NuclinoObject):
            return result
        elif isinstance(result, list):
            return [self.parse(li) for li in result]
        else:
            return source

    def get(self, path: str, params: dict = {}) -> Union[List, NuclinoObject, dict]:
        self.check_limit()
        response = self.session.get(join_url(self.base_url, path), params=params)
        return self._process_response(response)

    def delete(self, path: str) -> Union[List, NuclinoObject, dict]:
        self.check_limit()
        response = self.session.delete(join_url(self.base_url, path))
        return self._process_response(response)

    def post(self, path: str, data: dict) -> Union[List, NuclinoObject, dict]:
        headers = {'Content-Type': 'application/json'}
        self.check_limit()
        response = self.session.post(
            join_url(self.base_url, path),
            json=data,
            headers=headers
        )
        return self._process_response(response)

    def put(self, path: str, data: dict) -> Union[List, NuclinoObject, dict]:
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
    ) -> Union[List, NuclinoObject, dict]:
        '''
        Get list of teams available for user.

        :param limit: number between 1 and 100 to limit the results.
        :param after: only return teams that come after the given team ID.

        :returns: list of Team objects.
        '''

        path = '/teams'
        params = {}
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        return self.get(path, params)

    def get_team(self, team_id: str):
        '''
        Get specific team by ID.

        :param team_id: ID of the team to get.

        :returns: Team object.
        '''

        path = f'/teams/{team_id}'
        return self.get(path)

    def get_workspaces(
        self,
        team_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None
    ) -> Union[List, NuclinoObject, dict]:
        '''
        Get list of workspaces available for user.

        :param team_id: ID of the team the returned workspaces should belong to.
        :param limit: number between 1 and 100 to limit the results.
        :param after: only return workspaces that come after the given workspace
                      ID.

        :returns: list of Workspace objects.
        '''

        path = '/workspaces'
        params = {}
        if team_id is not None:
            params['teamId'] = team_id
        if limit is not None:
            params['limit'] = str(limit)
        if after is not None:
            params['after'] = after
        return self.get(path, params)

    def get_workspace(self, workspace_id: str) -> Union[List, NuclinoObject, dict]:
        '''
        Get specific workspace by ID.

        :param workspace_id: ID of the workspace to get.

        :returns: Workspace object.
        '''

        path = f'/workspaces/{workspace_id}'
        return self.get(path)

    def get_items(
        self,
        team_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: Optional[int] = None,
        after: Optional[str] = None,
        search: Optional[str] = None
    ) -> Union[List, NuclinoObject, dict]:
        '''
        Get list of items and collection from the team or the workspace. Either
        `team_id` or `workspace_id` parameter is required. This method is also
        used for item search, use `search` parameter.

        :param team_id: ID of the team the returned items should belong to.
        :param team_id: ID of the workspace the returned items should belong to.
        :param limit:   number between 1 and 100 to limit the results.
        :param after:   only return workspaces that come after the given workspace
                        ID.
        :param search:  search query.

        :returns: list of Item and Collection objects.
        '''

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

    def get_item(self, item_id: str) -> Union[List, NuclinoObject, dict]:
        '''
        Get specific item or collection by ID.

        :param item_id: ID of the item to get.

        :returns: Item or Collection object.
        '''

        path = f'/items/{item_id}'
        return self.get(path)

    def get_collection(self, collection_id: str) -> Union[List, NuclinoObject, dict]:
        '''
        Alias for get_item. Get specific item or collection by ID.

        :param item_id: ID of the item to get.

        :returns: Item or Collection object.
        '''

        return self.get_item(collection_id)

    def create_item(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        object: Optional[str] = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[List, NuclinoObject, dict]:
        '''
        Create a new item or collection in the workspace or as a child of a
        collection. Either `workspace_id` or `parent_id` parameter is required.

        :param workspace_id: ID of the workspace the item should be put in (will
                             be placed at the root of the workspace).
        :param parent_id:    ID of the collection the item should be put in.
        :param object:       'item' or 'collection'.
        :param title:        item or collection title.
        :param content:      item content (only for items).
        :param index:        where to put this item in the tree. If not
                             specified — will be put at the end.

        :returns: the created Item or Collection object.
        '''

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

    def create_collection(
        self,
        workspace_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        title: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[List, NuclinoObject, dict]:
        '''
        Create a collection in the workspace or as a child of another collection.
        Either `workspace_id` or `parent_id` parameter is required.

        :param workspace_id: ID of the workspace the collection should be put in
                             (will be placed at the root of the workspace).
        :param parent_id:    ID of the collection this collection should be put in.
        :param title:        collection title.
        :param index:        where to put this collection in the tree. If not
                             specified — will be put at the end.

        :returns: the created Collection object.
        '''

        return self.create_item(
            workspace_id=workspace_id,
            parent_id=parent_id,
            object='collection',
            title=title,
            content=None,
            index=index
        )

    def update_item(
        self,
        item_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None
    ) -> Union[List, NuclinoObject, dict]:
        '''
        Update item or collection.

        :param item_id: ID of the item to update.
        :param title:   new item title. If not specified — won't be changed.
        :param content: new item content (only for items). If not specified —
                        won't be changed.

        :returns: updated Item or Collection object.
        '''

        path = f'/items/{item_id}'
        data = {}
        if title is not None:
            data['title'] = title
        if content is not None:
            data['content'] = content
        return self.put(path, data=data)

    def update_collection(
        self,
        collection_id: str,
        title: Optional[str] = None
    ) -> Union[List, NuclinoObject, dict]:
        '''
        Update collection title.

        :param collection_id: ID of the collection to update.
        :param title:      new collection title. If not specified — won't be
                           changed.

        :returns: updated Collection object.
        '''

        return self.update_item(collection_id, title=title, content=None)

    def delete_item(self, item_id: str) -> Union[List, NuclinoObject, dict]:
        '''
        Move item or collection to trash.

        :param item_id: ID of the item to delete.

        :returns: a dictionary with ID of deleted item.
        '''
        path = f'/items/{item_id}'
        return self.delete(path)

    def delete_collection(self, collection_id: str) -> Union[List, NuclinoObject, dict]:
        '''
        Alias for delete_item. Move item or collection to trash.

        :param item_id: ID of the item to delete.

        :returns: a dictionary with ID of deleted item.
        '''

        return self.delete_item(collection_id)

    def get_file(self, file_id: str) -> Union[List, NuclinoObject, dict]:
        '''
        Get a file object by ID.

        :param item_id: ID of the file to get.

        :returns: a File object.
        '''

        path = f'/files/{file_id}'
        return self.get(path)
