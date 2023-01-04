from __future__ import annotations
from typing import List, Union, Optional, Callable


class NuclinoObject:
    _object = ''

    @classmethod
    def load(cls, props: dict, nuclino):
        return cls(props, nuclino)

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        self.data = dict(props)
        self.nuclino = nuclino


class Team(NuclinoObject):
    _object = "team"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        super().__init__(props, nuclino)

        self.id = props['id']
        self.url = props['url']
        self.name = props['name']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']

    def get_workspaces(self) -> List[Workspace]:
        '''
        Make an API call to get all workspaces that belong to this team.

        :returns: list of Workspace objects.
        '''

        return self.nuclino.get_workspaces(team_id=self.id)

    def __repr__(self) -> str:
        return f'<Team "{self.name}">'


class Workspace(NuclinoObject):
    _object = "workspace"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        super().__init__(props, nuclino)

        self.id = props['id']
        self.team_id = props['teamId']
        self.name = props['name']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']
        self.child_ids = props['childIds']

    def get_team(self) -> Team:
        '''
        Make an API call to get the team this workspace belongs to.

        :returns: Team object.
        '''

        return self.nuclino.get_team(self.team_id)

    def get_children(self) -> List[Union[Item, Collection]]:
        return [self.nuclino.get_item(id_) for id_ in self.child_ids]

    def create_item(
        self,
        object: Optional[str] = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Collection]:
        '''
        Create a new item or collection under this workspace.

        :param object:  'item' or 'collection'.
        :param title':  item title.
        :param content: item content (only for items).
        :param index:   where to put this item in the tree. If not
                        specified — will be put at the end.

        :returns: Item or Collection object.
        '''

        return self.nuclino.create_item(
            workspace_id=self.id,
            object=object,
            title=title,
            content=content,
            index=index
        )

    def create_collection(
        self,
        title: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Collection]:
        '''
        Create a new collection under this workspace.

        :param title':  collection title.
        :param index:   where to put this collection in the tree. If not
                        specified — will be put at the end.

        :returns: Collection object.
        '''

        return self.nuclino.create_item(
            workspace_id=self.id,
            object="collection",
            title=title,
            content=None,
            index=index
        )

    def __repr__(self) -> str:
        return f'<Workspace "{self.name}">'


class Collection(NuclinoObject):
    _object = "collection"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        super().__init__(props, nuclino)

        self.id = props['id']
        self.child_ids = props['childIds']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']
        self.last_updated_at = props['lastUpdatedAt']
        self.last_updated_user_id = props['lastUpdatedUserId']
        self.title = props['title']
        self.url = props['url']
        self.workspace_id = props['workspaceId']

    def get_children(self) -> List[Union[Item, Collection]]:
        '''
        Make an API call to get the list of direct children of this collection.

        :returns: list of Item and Collection objects.
        '''

        return [self.nuclino.get_item(id_) for id_ in self.child_ids]

    def get_workspace(self) -> Workspace:
        '''
        Make an API call to get the workspace this collection belongs to.

        :returns: Workspace object.
        '''

        return self.nuclino.get_workspace(self.workspace_id)

    def create_item(
        self,
        object: Optional[str] = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Collection]:
        '''
        Create an item or a collection under this collection.

        :param object:  'item' or 'collection'.
        :param title:   item title.
        :param content: item content.
        :param index:   where to put this item in the tree. If not
                        specified — will be put at the end.

        :returns: created Item or Collection object.
        '''

        return self.nuclino.create_item(
            parent_id=self.id,
            object=object,
            title=title,
            content=content,
            index=index
        )

    def create_collection(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Collection]:
        '''
        Create another collection under this collection.

        :param title:   collection title.
        :param index:   where to put this collection in the tree. If not
                        specified — will be put at the end.

        :returns: created Collection object.
        '''

        return self.nuclino.create_item(
            parent_id=self.id,
            object="collection",
            title=title,
            index=index
        )

    def delete(self) -> dict:
        '''
        Move this collection to trash.

        :returns: dictionary with this collection ID.
        '''

        return self.nuclino.delete_collection(self.id)

    def update(
        self,
        title: Optional[str] = None
    ):
        '''
        Change this collection title.

        :param title: new title value.

        :returns: updated Collection object.
        '''

        return self.nuclino.update_collection(self.id, title)

    def __repr__(self) -> str:
        return f'<Collection "{self.title}">'


class Item(NuclinoObject):
    _object = "item"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        super().__init__(props, nuclino)

        self.id = props['id']
        self.content_meta = props['contentMeta']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']
        self.last_updated_at = props['lastUpdatedAt']
        self.last_updated_user_id = props['lastUpdatedUserId']
        self.title = props['title']
        self.url = props['url']
        self.workspace_id = props['workspaceId']
        self.content = props.get('content')

    def get_workspace(self) -> Workspace:
        '''
        Make an API call to get the workspace this item belongs to.

        :returns: Workspace object.
        '''

        return self.nuclino.get_workspace(self.workspace_id)

    def get_items(self) -> List[Union[Item, Collection]]:
        '''
        Make API calls to get list of items or collections that are referenced in
        this item.

        :returns: list of Item or Collection objects.
        '''

        return [self.nuclino.get_item(id_) for id_ in self.content_meta['itemIds']]

    def get_files(self) -> List[File]:
        '''
        Make API calls to get the list of files attached to this file.

        :returns: list of File objects.
        '''

        return [self.nuclino.get_file(id_) for id_ in self.content_meta['fileIds']]

    def delete(self) -> dict:
        '''
        Move this item to trash.

        :returns: dictionary with this item id.
        '''

        return self.nuclino.delete_item(self.id)

    def update(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None
    ):
        '''
        Update this item.

        :param title:   new item title.
        :param content: new item content.

        returns: updated Item object.
        '''

        return self.nuclino.update_item(self.id, title, content)

    def __repr__(self):
        return f'<Item "{self.title}">'


class File(NuclinoObject):
    _object = "file"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        super().__init__(props, nuclino)

        self.id = props['id']
        self.item_id = props['itemId']
        self.file_name = props['fileName']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']
        self.download = props['download']

    def get_item(self) -> Item:
        '''
        Make an API call to get the item this file is attached to.

        :returns: Item object.
        '''

        return self.nuclino.get_item(self.item_id)

    def __repr__(self):
        return f'<file "{self.file_name}">'


def load_list(props: dict, nuclino):
    if props['object'] != 'list':
        raise RuntimeError("Wrong object")
    else:
        return props['results']


def get_loader(name: str) -> Callable:
    classes = {
        'list': load_list,
    }
    classes.update(
        {no._object: no.load for no in NuclinoObject.__subclasses__()}
    )
    return classes[name]
