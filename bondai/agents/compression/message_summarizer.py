import os
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed
from bondai.models import LLM
from bondai.prompt import PromptBuilder, JinjaPromptBuilder
from bondai.util import load_local_resource
from bondai.agents.messages import AgentMessage, ConversationMessage, ToolUsageMessage

MIN_SUMMARIZABLE_LENGTH = 250
DEFAULT_SUMMARY_PROMPT_TEMPLATE = load_local_resource(
    __file__, os.path.join("prompts", "message_summarizer_prompt_template.md")
)


def summarize_messages(
    llm: LLM,
    messages: List[AgentMessage],
    message_prompt_builder: PromptBuilder,
    summary_prompt_builder: PromptBuilder = JinjaPromptBuilder(
        DEFAULT_SUMMARY_PROMPT_TEMPLATE
    ),
    max_summary_words: int = 100,
) -> List[AgentMessage]:
    summarizable_messages = [
        m
        for m in messages
        if (
            isinstance(m, ConversationMessage)
            and not m.message_summary
            and len(m.message) > MIN_SUMMARIZABLE_LENGTH
        )
        or (
            isinstance(m, ToolUsageMessage)
            and not m.tool_output_summary
            and len(m.tool_output) > MIN_SUMMARIZABLE_LENGTH
        )
    ]

    print(f"Summarizing {len(summarizable_messages)} messages...")

    # Creating a thread pool executor to parallelize summary generation
    with ThreadPoolExecutor() as executor:
        futures = []
        for m in summarizable_messages:
            # Find all messages that occurred before the current message
            previous_messages = [msg for msg in messages if msg.timestamp < m.timestamp]
            # Submit the _summarize_message task to the executor
            future = executor.submit(
                _summarize_message,
                m,
                previous_messages[-5:],
                llm,
                summary_prompt_builder,
                message_prompt_builder,
                max_summary_words,
            )
            futures.append(future)

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                print(f"Message summary generation generated an exception: {exc}")

    return messages


def _summarize_message(
    message: AgentMessage,
    previous_messages: List[AgentMessage],
    llm: LLM,
    prompt_builder: PromptBuilder,
    message_prompt_builder: PromptBuilder,
    max_summary_words: int,
) -> str:
    message_prompt = message_prompt_builder.build_prompt(message=message)
    previous_message_prompts = [
        message_prompt_builder.build_prompt(
            message=msg,
        )
        for msg in previous_messages
    ]

    prompt = prompt_builder.build_prompt(
        message=message_prompt,
        previous_messages=previous_message_prompts,
        max_words=max_summary_words,
    )

    summary, _ = llm.get_completion(messages=[{"role": "system", "content": prompt}])

    # print("************")
    # print(f"Message: {message_prompt}")
    # print(f"Summary: {summary}")
    # print("************")
    if isinstance(message, ConversationMessage):
        print("Updating message summary...")
        message.message_summary = summary
    elif isinstance(message, ToolUsageMessage):
        message.tool_output_summary = summary
    # print(message)
