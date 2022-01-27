# PyNuclino

PyNuclino is wrapper for [Nuclino API](https://help.nuclino.com/d3a29686-api).

## Installation

```bash
pip3 install pynuclino
```

## Usage

Initialize the `Nuclino` object with your API key ([getting API key](https://help.nuclino.com/04598850-manage-api-keys)):

```python
>>> from nuclino import Nuclino
>>> client = Nuclino('your-api-key')
```

Get some data:

```python
>>> client.get_workspaces()
[<Workspace "Support">, <Workspace "Projects">, ...]
>>> client.get_teams()
[<Team "MyTeam">, <Team "TheirTeam">]
>>> client.get_items(team_id='your_team_id')
[<Item "Home office allowance">, <Cluster "Leave">, <Item "Welcome!">, ...]
```

Objects have attributes:

```python
>>> item = client.get_item('item_id')
>>> i1.title
'Home office allowance'
>>> i1.created_at
'2022-01-26T16:32:41.981Z'
```

Attribute names correspond to the JSON field names, but in Python variable format: `createdAt` -> `created_at`.

Objects also have convenience methods:

```python
>>> team.get_workspaces()
[<Workspace "Support">, <Workspace "Projects">, ...]
>>> workspace.get_children()
[<Cluster "Product FAQ">, <Cluster "Canned responses">, ...]
>>> item.get_files()
[<file "6e54474a.png">, <file "c414f936.png">, ...]
```

You can update or delete items using Item object methods:

```python
>>> item = client.get_item('item_id')
>>> item.update(title='New Title', content='# New content\n')
<Item "New Title">
>>> item.delete()
{'id': 'fe94a28d-6c5c-4969-9ee7-7d6433f74adf'}
```

Full reference of methods and attributes is below.

## Rate limiting

Nuclino API usage is currently [rate limited](https://help.nuclino.com/b147124e-rate-limiting) to 150 requests per minute. PyNuclino uses [ratelimit](https://github.com/tomasbasham/ratelimit) library to handle rate limiting.

Default request limit is set to 140 req/min. To change it set the `requests_per_minute` init parameter:

```python
>>> client = Nuclino('your-api-key', requests_per_minute=100)
```

## Reference

### Nuclino

`Nuclino(api_key, base_url, requests_per_minute)`


Nuclino is the main object that connects you to Nuclino api.

Initialization parameters:

* `api_key` (string, required) — your personal API key ([how to get an API key](https://help.nuclino.com/04598850-manage-api-keys)).
* `base_url` (string, optional) — base url for Nuclino API calls. Default: `https://api.nuclino.com/v0`.
* `requests_per_minute` (int, optional) — number of requests the client will allow to send per minute. If this limit is exceeded, client will wait for some time before sending next request. Default: `140`.

**Methods**

`get_teams(limit=None, after=None)`

List teams that you have access to. Returns list of Team objects.

`get_team(team_id)`

Get a team by id. Returns a single Team object.

`get_workspaces(limit=None, after=None)`

List workspaces that you have access to. Returns list of Workspace objects.

`get_workspace(team_id)`

Get a workspace by id. Returns a single Workspace object.

`get_items(team_id=None, workspace_id=None, limit=None, after=None, search=None)`

Get list of items in team or workspace. You must supply either `team_id` or `workspace_id`. Add search query in `search` parameter to search items. Returns list of Item and Cluster objects.

`get_item(item_id)`

Get item or cluster by ID. Returns a single Item or Cluster object.

`get_cluster(cluster_id)`

Alias for `get_item` method, works the same.

`create_item(workspace_id=None, parent_id=None, object='item', title=None, content=None, index=None)`

Create a new item or cluster (depending on the `object` param value). You must supply either `workspace_id` or `parent_id`.

`create_cluster(workspace_id=None, parent_id=None, title=None, index=None)`

Create a new cluster. You must supply either `workspace_id` or `parent_id`.

`update_item(item_id, title=None, content=None)`

Update item or cluster. If `title` or `content` is none, it won't be changed.

`update_cluster(cluster_id, title=None)`

Update cluster title.

`delete_title(item_id)`

Delete item or cluster.

`delete_cluster(cluster_id)`

Alias for `delete_item` method, works the same.

`get_file(file_id)`

Get a file by id. Returns a single File instance.

### Team

**Attributes**

* `id` (str) — team id,
* `url` (str) — team url,
* `name` (str) — team name,
* `created_at` (str) — date created in ISO 8601 format,
* `created_user_id` (str) — id of the user who created this team.

**Methods**

`get_workspaces()`

Make an API call to get list of workspaces this team has.

### Workspace

**Attrubutes**

* `id` (str) — workspace id,
* `team_id` (str) — id of the team this workspace belongs to,
* `name` (str) — workspace name,
* `created_at` (str) — date created in ISO 8601 format,
* `created_user_id` (str) — id of the user who created this workspace,
* `child_ids` (list) — list of ids of top level items and clusters from this workspace.

**Methods**

`get_team()`

Make an API call to get the team this workspace belongs to.

`get_children()`

Make API calls to get a list of top level itesm and clusters from this workspace. Returns list of Item and Cluster objects.

`create_item(object='item', title=None, content=None, index=None)`

Create an item or a cluster (depending on the `object` param) in this workspace.

`create_cluster(title=None, index=None)`

Create a cluster in this workspace.

### Cluster

**Attributes**

* `id` (str) — cluster id,
* `child_ids` (list) — list of ids of items or clusters that belong to this cluster (only top level),
* `created_at` (str) — date created in ISO 8601 format,
* `created_user_id` (str) — id of the user who created the cluster,
* `last_updated_at` (str) — date last update in ISO 8601 format,
* `last_updated_user_id` (str) — id of the user who last updated the cluster,
* `title` (str) — cluster title,
* `url` (str) — cluster url,
* `workspace_id` (str) — id of the workspace this cluster belongs to.

**Methods**

`get_children()`

Make API calls to get list of items and clusters that belong to this cluster (only top level). Returns list of Item and Cluster objects.

`get_workspace()`

Make an API call to get the workspace this cluster belongs to.

`create_item(object='item', title=None, content=None, index=None)`

Create an item or a cluster (depending on the `object` param) under this cluster.

`create_cluster(title=None, index=None)`

Create a cluster under this cluster.

`delete()`

Delete this cluster.

`update(title)`

Update this cluster title.

### Item

* `id` (str) — item id,
* `content_meta` (dict) — item meta dictionary,
* `created_at` (str) — date created in ISO 8601 format,
* `created_user_id` (str) — id of the user who created the item,
* `last_updated_at` (str) — date updated in ISO 8601 format,
* `last_updated_user_id` (str) — id of the user who last updated the item,
* `title` (str) — item title,
* `url` (str) — item url,
* `workspace_id` (str) — id of the workspace this item belongs to,
* `content` (str) — item content in Markdown (to get content use `get_item`, not `get_items`).

**Methods**

`get_workspace()`

Make an API call to get the workspace this item belongs to.

`get_items()`

Make API calls to get list of items that are referenced inside this item. Returns list of Item objects.

`get_files()`

Make API calls to get list of files that are attached to this item. Returns list of File objects.

`delete()`

Delete this item.

`update(title: None, content: None)`

Update this item. Title or content won't be changed if corresponding param is empty.

### File

**Attributes**

* `id` (str) — file id,
* `item_id` (str) — id of the item this file is attached to,
* `file_name` (str) — file name,
* `created_at` (str) — date created in ISO 8601 format,
* `created_user_id` (str) — id of the user who created the file,
* `download` (dict) — dictionary with download link and expiry date.

**Methods**

`get_item()`

Make an API call to get the item this file is attached to.
