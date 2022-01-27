from __future__ import annotations
from typing import List, Union, Optional


class NuclinoObject:
    _object = None

    @classmethod
    def load(cls, source: dict, nuclino):
        return cls(props=source, nuclino=nuclino)


class Team(NuclinoObject):
    _object = "team"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        self.data = dict(props)
        self.nuclino = nuclino

        self.id = props['id']
        self.url = props['url']
        self.name = props['name']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']

    def get_workspaces(self) -> List[Workspace]:
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
        self.data = dict(props)
        self.nuclino = nuclino

        self.id = props['id']
        self.team_id = props['teamId']
        self.name = props['name']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']
        self.child_ids = props['childIds']

    def get_team(self) -> Team:
        return self.nuclino.get_team(self.team_id)

    def get_children(self) -> List[Union[Item, Cluster]]:
        return [self.nuclino.get_item(id_) for id_ in self.child_ids]

    def create_item(
        self,
        object: Optional[str] = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Cluster]:
        return self.nuclino.create_item(
            workspace_id=self.id,
            object=object,
            title=title,
            content=content,
            index=index
        )

    def create_cluster(
        self,
        title: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Cluster]:
        return self.nuclino.create_item(
            workspace_id=self.id,
            object="cluster",
            title=title,
            content=None,
            index=index
        )

    def __repr__(self) -> str:
        return f'<Workspace "{self.name}">'


class Cluster(NuclinoObject):
    _object = "cluster"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        self.data = dict(props)
        self.nuclino = nuclino

        self.id = props['id']
        self.child_ids = props['childIds']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']
        self.last_updated_at = props['lastUpdatedAt']
        self.last_updated_user_id = props['lastUpdatedUserId']
        self.title = props['title']
        self.url = props['url']
        self.workspace_id = props['workspaceId']

    def get_children(self) -> List[Union[Item, Cluster]]:
        return [self.nuclino.get_item(id_) for id_ in self.child_ids]

    def get_workspace(self) -> Workspace:
        return self.nuclino.get_workspace(self.workspace_id)

    def create_item(
        self,
        object: Optional[str] = 'item',
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Cluster]:
        return self.nuclino.create_item(
            parent_id=self.id,
            object=object,
            title=title,
            content=content,
            index=index
        )

    def create_cluster(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None,
        index: Optional[int] = None
    ) -> Union[Item, Cluster]:
        return self.nuclino.create_item(
            parent_id=self.id,
            object="cluster",
            title=title,
            index=index
        )

    def delete(self) -> dict:
        return self.nuclino.delete_cluster(self.id)

    def update(
        self,
        title: Optional[str] = None
    ):
        return self.nuclino.update_cluster(self.id, title)

    def __repr__(self) -> str:
        return f'<Cluster "{self.title}">'


class Item(NuclinoObject):
    _object = "item"

    def __init__(
        self,
        props: dict,
        nuclino
    ):
        self.data = dict(props)
        self.nuclino = nuclino

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
        return self.nuclino.get_workspace(self.workspace_id)

    def get_items(self) -> List[Union[Item, Cluster]]:
        return [self.nuclino.get_item(id_) for id_ in self.content_meta['itemIds']]

    def get_files(self) -> List[File]:
        return [self.nuclino.get_file(id_) for id_ in self.content_meta['fileIds']]

    def delete(self) -> dict:
        return self.nuclino.delete_item(self.id)

    def update(
        self,
        title: Optional[str] = None,
        content: Optional[str] = None
    ):
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
        self.data = dict(props)
        self.nuclino = nuclino

        self.id = props['id']
        self.item_id = props['itemId']
        self.file_name = props['fileName']
        self.created_at = props['createdAt']
        self.created_user_id = props['createdUserId']
        self.download = props['download']

    def get_item(self) -> Item:
        return self.nuclino.get_item(self.item_id)

    def __repr__(self):
        return f'<file "{self.file_name}">'


def load_list(source: dict, nuclino) -> list:
    if source['object'] != 'list':
        raise RuntimeError("Wrong object")
    else:
        return source['results']


def get_loader(name: str) -> NuclinoObject:
    classes = {
        'list': load_list,
    }
    classes.update(
        {no._object: no.load for no in NuclinoObject.__subclasses__()}
    )
    return classes[name]
