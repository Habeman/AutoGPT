from logging import Logger

from autogpts.autogpt.autogpt.core.agents.base.features.agentmixin import \
    AgentMixin


class ToolExecutor(AgentMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Logger(name=__name__).warning("ToolExecutor : Has not been implemented yet")
