import os
from typing import List
from bondai.models import LLM
from bondai.prompt import PromptBuilder, JinjaPromptBuilder
from bondai.util import load_local_resource
from bondai.agents.messages import (
    AgentMessage,
    SummaryMessage,
)

DEFAULT_SUMMARY_PROMPT_TEMPLATE = load_local_resource(
    __file__, os.path.join("prompts", "conversation_summarizer_prompt_template.md")
)


def summarize_conversation(
    llm: LLM,
    messages: List[AgentMessage],
    message_prompt_builder: PromptBuilder,
    summary_prompt_builder: PromptBuilder = JinjaPromptBuilder(
        DEFAULT_SUMMARY_PROMPT_TEMPLATE
    ),
) -> AgentMessage:
    if not messages:
        return []

    # Format the messages
    message_prompts = [
        message_prompt_builder.build_prompt(
            message=msg,
        )
        for msg in messages
    ]

    # Get the summary for the entire conversation
    prompt = summary_prompt_builder.build_prompt(messages=message_prompts)
    summary, _ = llm.get_completion(messages=[{"role": "system", "content": prompt}])

    # Return the summary wrapped in an SummaryMessage
    return SummaryMessage(
        message=summary,
        children=list(messages),
        timestamp=messages[-1].timestamp,
    )
