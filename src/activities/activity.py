"""Define base Activity object."""

from dataclasses import dataclass, field
from typing import Optional, Dict, Union, Sequence, Tuple
from uuid import UUID, uuid4

from activities.core import HasInputOutput
from activities.outputs import Outputs
from activities.reference import Reference
from activities.task import Task


@dataclass
class Activity(HasInputOutput):

    name: str
    tasks: Union[Sequence["Activity"], Sequence[Task]]
    outputs: Optional[Outputs] = None
    host: Optional[UUID] = None
    uuid: UUID = field(default_factory=uuid4)
    config: Dict = field(default_factory=dict)
    output_sources: Optional[Outputs] = field(default=None, init=False)

    def __post_init__(self):
        task_types = set(map(type, self.tasks))
        if len(task_types) != 1:
            raise ValueError(
                "Activity tasks must either be all Task objects or all Activity objects"
            )

        if self.contains_activities:
            for task in self.tasks:
                if task.host is not None:
                    raise ValueError(
                        f"Subactivity {task} already belongs to another activity"
                    )
                task.host = self.uuid

        if self.outputs is not None:
            self.output_sources = self.outputs
            self.outputs = self.outputs.reference(self.uuid)

    @property
    def task_type(self) -> str:
        return "activity" if isinstance(self, Activity) else "task"

    @property
    def contains_activities(self) -> bool:
        return self.task_type == "activity"

    @property
    def input_references(self) -> Tuple[Reference, ...]:
        references = set()
        task_uuids = set()
        for task in self.tasks:
            references.update(task.input_references)
            task_uuids.add(task.uuid)

        return tuple([ref for ref in references if ref.uuid not in task_uuids])

    @property
    def output_references(self) -> Tuple[Reference, ...]:
        if self.output_sources is None:
            return tuple()
        return self.output_sources.references

    @property
    def activity_graph(self):
        from activities.graph import activity_output_graph, activity_input_graph
        import networkx as nx

        if self.contains_activities:
            graph = activity_output_graph(self)
            activity_graphs = [task.activity_graph for task in self.tasks]
            return nx.compose_all(activity_graphs + [graph])

        else:
            return activity_input_graph(self)

    @property
    def task_graph(self):
        from activities.graph import activity_output_graph, task_graph
        import networkx as nx

        if self.contains_activities:
            graph = activity_output_graph(self)
            activity_graphs = [activity.task_graph for activity in self.tasks]
            return nx.compose_all(activity_graphs + [graph])

        else:
            return task_graph(self)
