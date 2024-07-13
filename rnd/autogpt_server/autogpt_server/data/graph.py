import asyncio
import uuid
from typing import Any, Literal

import prisma.types
from prisma.models import AgentGraph, AgentNode, AgentNodeLink
from pydantic import BaseModel, PrivateAttr, field_validator

from autogpt_server.data.db import BaseDbModel
from autogpt_server.util import json


class Link(BaseModel):
    source_id: str
    sink_id: str
    source_name: str
    sink_name: str

    def __init__(self, source_id: str, sink_id: str, source_name: str, sink_name: str):
        super().__init__(
            source_id=source_id,
            sink_id=sink_id,
            source_name=source_name,
            sink_name=sink_name,
        )

    @staticmethod
    def from_db(link: AgentNodeLink):
        return Link(
            source_name=link.sourceName,
            source_id=link.agentNodeSourceId,
            sink_name=link.sinkName,
            sink_id=link.agentNodeSinkId,
        )

    def __hash__(self):
        return hash((self.source_id, self.sink_id, self.source_name, self.sink_name))


class Node(BaseDbModel):
    block_id: str
    input_default: dict[str, Any] = {}  # dict[input_name, default_value]
    metadata: dict[str, Any] = {}

    _input_links: list[Link] = PrivateAttr(default=[])
    _output_links: list[Link] = PrivateAttr(default=[])

    @property
    def input_links(self) -> list[Link]:
        return self._input_links

    @property
    def output_links(self) -> list[Link]:
        return self._output_links

    @staticmethod
    def from_db(node: AgentNode):
        if not node.AgentBlock:
            raise ValueError(f"Invalid node {node.id}, invalid AgentBlock.")
        obj = Node(
            id=node.id,
            block_id=node.AgentBlock.id,
            input_default=json.loads(node.constantInput),
            metadata=json.loads(node.metadata),
        )
        obj._input_links = [Link.from_db(link) for link in node.Input or []]
        obj._output_links = [Link.from_db(link) for link in node.Output or []]
        return obj


class Graph(BaseModel):
    graph_id: str = ""
    version: int = 1
    is_active: bool = True
    is_template: bool = False
    name: str
    description: str
    nodes: list[Node]
    links: list[Link]

    @field_validator("graph_id", mode="before")
    def set_graph_id(cls, graph_id: str) -> str:
        return graph_id or str(uuid.uuid4())

    @property
    def starting_nodes(self) -> list[Node]:
        outbound_nodes = {link.sink_id for link in self.links}
        return [node for node in self.nodes if node.id not in outbound_nodes]

    @staticmethod
    def from_db(graph: AgentGraph):
        return Graph(
            graph_id=graph.graph_id,
            version=graph.version,
            is_active=graph.is_active,
            is_template=graph.is_template,
            name=graph.name or "",
            description=graph.description or "",
            nodes=[Node.from_db(node) for node in graph.AgentNodes or []],
            links=list(
                {
                    Link.from_db(link)
                    for node in graph.AgentNodes or []
                    for link in (node.Input or []) + (node.Output or [])
                }
            ),
        )


class GraphMeta(BaseModel):
    graph_id: str
    version: int
    name: str
    description: str
    is_active: bool
    is_template: bool

    @staticmethod
    def from_db(graph: AgentGraph):
        return GraphMeta(
            graph_id=graph.graph_id,
            version=graph.version,
            name=graph.name or "",
            description=graph.description or "",
            is_active=graph.is_active,
            is_template=graph.is_template,
        )


EXECUTION_NODE_INCLUDE = {
    "Input": True,
    "Output": True,
    "AgentBlock": True,
}


# --------------------- Model functions --------------------- #


async def get_node(node_id: str) -> Node | None:
    node = await AgentNode.prisma().find_unique_or_raise(
        where={"id": node_id},
        include=EXECUTION_NODE_INCLUDE,  # type: ignore
    )
    return Node.from_db(node) if node else None


# TODO: Delete this
async def get_graph_ids() -> list[str]:
    return [
        graph.graph_id
        for graph in await AgentGraph.prisma().find_many(where={"is_template": False})
    ]  # type: ignore


async def get_graphs_meta(
    filter_by: Literal["is_active", "is_template"] | None = "is_active"
) -> list[GraphMeta]:
    """
    Retrieves graph metadata objects.
    Default behaviour is to get all currently active graphs.

    Args:
        filter: An optional filter to either select templates or active graphs.

    Returns:
        list[GraphMeta]: A list of GraphMeta objects representing the retrieved graph metadata.
    """
    where_clause: prisma.types.AgentGraphWhereInput = {}

    if filter_by:
        where_clause[filter_by] = True

    graphs = await AgentGraph.prisma().find_many(
        where=where_clause,
        distinct=["graph_id"] if filter_by else None,
        order={"version": "desc"},
    )

    if not graphs:
        return []

    return [GraphMeta.from_db(graph) for graph in graphs]


async def get_graph(graph_id: str, version: int | None = None) -> Graph:
    """
    Retrieves a graph from the DB.
    Defaults to the current active version if `version` is not passed.
    """
    where_clause: prisma.types.AgentGraphWhereInput = {"graph_id": graph_id}
    if version is not None:
        where_clause["version"] = version
    else:
        where_clause["is_active"] = True

    graph = await AgentGraph.prisma().find_first_or_raise(
        where=where_clause,
        include={"AgentNodes": {"include": EXECUTION_NODE_INCLUDE}},  # type: ignore
        distinct=["graph_id"] if not version else None,
        order={"version": "desc"},
    )
    return Graph.from_db(graph)


async def set_graph_active_version(graph_id: str, version: int) -> None:
    updated_graph = await AgentGraph.prisma().update(
        data={"is_active": True},
        where={"id": {"graph_id": graph_id, "version": version}},
    )
    if not updated_graph:
        raise Exception(f"Graph #{graph_id} v{version} not found")

    # Deactivate all other versions
    await AgentGraph.prisma().update_many(
        data={"is_active": False},
        where={"graph_id": graph_id, "version": {"not": version}},
    )


async def get_graph_all_versions(graph_id: str) -> list[Graph]:
    graph_history = await AgentGraph.prisma().find_many(
        where={"graph_id": graph_id},
        order={"version": "desc"},
        include={"AgentNodes": {"include": EXECUTION_NODE_INCLUDE}},  # type: ignore
    )

    if not graph_history:
        return []

    return [Graph.from_db(graph) for graph in graph_history]


async def create_graph(graph: Graph) -> Graph:
    await AgentGraph.prisma().create(
        data={
            "graph_id": graph.graph_id,
            "version": graph.version,
            "name": graph.name,
            "description": graph.description,
            "is_template": graph.is_template,
            "is_active": graph.is_active,
        }
    )

    # TODO: replace bulk creation using create_many
    await asyncio.gather(
        *[
            AgentNode.prisma().create(
                {
                    "id": node.id,
                    "agentBlockId": node.block_id,
                    "agentGraphId": graph.graph_id,
                    "agentGraphVersion": graph.version,
                    "constantInput": json.dumps(node.input_default),
                    "metadata": json.dumps(node.metadata),
                }
            )
            for node in graph.nodes
        ]
    )

    await asyncio.gather(
        *[
            AgentNodeLink.prisma().create(
                {
                    "id": str(uuid.uuid4()),
                    "sourceName": link.source_name,
                    "sinkName": link.sink_name,
                    "agentNodeSourceId": link.source_id,
                    "agentNodeSinkId": link.sink_id,
                }
            )
            for link in graph.links
        ]
    )

    if created_graph := await get_graph(graph.graph_id, graph.version):
        return created_graph

    raise ValueError(f"Failed to create graph {graph.graph_id}:{graph.version}.")
