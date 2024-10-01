from langchain_core.messages import HumanMessage, SystemMessage
from config import config
from langchain.prompts import ChatPromptTemplate
from logger import setup_logger
from utils import (
    history_as_text,
)
from prompts import (
    condenser_system_prompt,
)
from models import get_model


logger = setup_logger(__name__)


async def invoke(message):
    logger.info(message)
    try:
        # important to await the result before returning
        return await query_chain(message)
    except Exception as inst:
        logger.exception(inst)
        return f"{message['displayName']} - the Alkemio's VirtualContributor is currently unavailable."


# how do we handle languages? not all spaces are in Dutch obviously
# translating the question to the data _base language_ should be a separate call
# so the translation could be used for embeddings retrieval
async def query_chain(message):
    model = get_model(message["engine"], message["externalConfig"]["apiKey"])
    question = message["question"]

    # # use the last N message from the history except the last one
    # # as it is the question we are answering now
    history = message["history"][(config["history_length"] + 1) * -1 : -1]

    # if we have history try to add context from it into the last question
    # - who is Maxima?
    # - Maxima is the Queen of The Netherlands
    # - born? =======> rephrased to: tell me about the birth of Queen Máxima of the Netherlands
    if len(history) > 0:
        logger.info(f"We have history. Let's rephrase. Length is: {len(history)}.")
        condenser_messages = [("system", condenser_system_prompt)]
        condenser_promt = ChatPromptTemplate.from_messages(condenser_messages)
        condenser_chain = condenser_promt | model

        result = condenser_chain.invoke(
            {"question": question, "chat_history": history_as_text(history)}
        )
        logger.info(
            f"Original question is: '{question}'; Rephrased question is: '{result.content}'"
        )
        question = result.content
    else:
        logger.info("No history to handle, initial interaction")

    messages = []

    for system_message in message["prompt"]:
        messages.append(SystemMessage(content=system_message))

    messages.append(HumanMessage(content=question))

    response = model.invoke(messages)
    return response.content
