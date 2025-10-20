import asyncio
import os
from config import env
import ai_adapter

from alkemio_virtual_contributor_engine import (
    AlkemioVirtualContributorEngine,
    Input,
    Response,
    setup_logger
)


logger = setup_logger(__name__)

logger.info(f"log level {os.path.basename(__file__)}: {env.log_level}")


async def on_request(input: Input) -> Response:
    logger.info(f"Expert engine invoked; Input is {input.model_dump()}")
    logger.info(
        f"AiPersonaServiceID={input.persona_id} with VC name `{input.display_name}` invoked."
    )
    result = await ai_adapter.invoke(input)
    logger.info(f"LLM result: {result.model_dump()}")
    return result


engine = AlkemioVirtualContributorEngine()
engine.register_handler(on_request)
asyncio.run(engine.start())
