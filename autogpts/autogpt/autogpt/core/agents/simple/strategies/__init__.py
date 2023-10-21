from logging import Logger
from autogpt.core.prompting.base import PromptStrategiesConfiguration

from autogpt.core.agents.simple.strategies.initial_plan import (
    InitialPlanStrategy,
    InitialPlanStrategyConfiguration,
)

from autogpt.core.agents.simple.strategies.select_tool import (
    SelectToolStrategy,
    SelectToolStrategyConfiguration,
)


class StrategiesConfiguration(PromptStrategiesConfiguration):
    initial_plan: InitialPlanStrategyConfiguration
    select_tool: SelectToolStrategyConfiguration


class Strategies:
    from autogpt.core.prompting.base import BasePromptStrategy, AbstractPromptStrategy

    @staticmethod
    def get_strategies(logger: Logger) -> list[AbstractPromptStrategy]:
        return [
            InitialPlanStrategy(
                logger=logger, **InitialPlanStrategy.default_configuration.dict()
            ),
            SelectToolStrategy(logger=logger, **SelectToolStrategy.default_configuration.dict()),
        ]
