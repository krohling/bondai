#!/usr/bin/env python3
import os
import argparse
from termcolor import cprint
from bondai.util import ModelLogger
from bondai.api import BondAIAPIServer
from bondai.models import LLM
from bondai.tools import AgentTool
from bondai.agents import (
    Agent,
    AgentEventNames,
    ConversationalAgent,
    BudgetExceededException,
)
from bondai.agents.group_chat import GroupConversation, UserProxy
from bondai.models.openai import (
    OpenAILLM,
    OpenAIModelNames,
    OpenAIConnectionType,
    enable_logging,
    OPENAI_CONNECTION_TYPE,
)
from bondai.memory import (
    MemoryManager,
    PersistentCoreMemoryDataSource,
    InMemoryCoreMemoryDataSource,
)
from .default_tools import load_all_tools
from .personas import (
    user_liaison_agent as user_liaison_profile,
)

if OPENAI_CONNECTION_TYPE == OpenAIConnectionType.OPENAI and not os.environ.get(
    "OPENAI_API_KEY"
):
    cprint(
        f"The OPENAI_API_KEY environment variable has not been set. Please input your OpenAI API Key now or type 'exit'.",
        "yellow",
    )
    user_input = input()
    if user_input == "exit":
        exit(1)
    else:
        import openai

        openai.api_key = user_input


parser = argparse.ArgumentParser(description="BondAI CLI tool options")

# --server with optional port
parser.add_argument(
    "--server",
    nargs="?",
    const="2663",
    metavar="server_port",
    help="Starts the BondAI web server. If no port is specified, defaults to 5000.",
)

# --enable-prompt-logging with optional log_dir
parser.add_argument(
    "--enable-prompt-logging",
    nargs="?",
    const="logs",
    metavar="log_dir",
    help='Turns on prompt logging which will write all prompt inputs into the specified directory. Defaults to "logs" if no directory provided.',
)

# --quiet
parser.add_argument(
    "--quiet",
    action="store_true",
    default=False,
    help="If set, minimizes the output to the console.",
)

args = parser.parse_args()


if args.enable_prompt_logging:
    log_dir = args.enable_prompt_logging
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    enable_logging(ModelLogger(log_dir))
    cprint(f"Prompt logging is enabled. Logs will be written to: {log_dir}", "yellow")


def build_agents(llm: LLM) -> GroupConversation:
    task_execution_agent = Agent(
        llm=llm,
        tools=load_all_tools(),
        max_tool_retries=5,
        memory_manager=MemoryManager(
            core_memory_datasource=InMemoryCoreMemoryDataSource(
                sections={"task": "No information is stored about the current task."},
                max_section_size=10000,
            )
        ),
    )

    user_liaison_agent = ConversationalAgent(
        llm=llm,
        name=user_liaison_profile.NAME,
        persona=user_liaison_profile.PERSONA,
        persona_summary=user_liaison_profile.PERSONA_SUMMARY,
        instructions=user_liaison_profile.INSTRUCTIONS,
        tools=[AgentTool(task_execution_agent)],
        memory_manager=MemoryManager(
            core_memory_datasource=PersistentCoreMemoryDataSource(
                file_path="./.memory/user_liason_core_memory.json",
                sections={"user": "No information is stored about the user."},
            )
        ),
    )

    return task_execution_agent, user_liaison_agent


def run_cli():
    cprint(f"Loading BondAI...", "white")
    try:
        llm = OpenAILLM(OpenAIModelNames.GPT4_0613)
        if args.server:
            port = int(args.server)
            server = BondAIAPIServer(port=port, agent_builder=lambda: build_agents(llm))

            try:
                server.run()
            except KeyboardInterrupt:
                cprint(f"\n\nStopping BondAI server...\n", "red")
        else:
            try:
                user_proxy = UserProxy(parse_recipients=False)
                task_execution_agent, user_liaison_agent = build_agents(llm)
                group_conversation = GroupConversation(
                    conversation_members=[user_proxy, user_liaison_agent]
                )

                @task_execution_agent.on(AgentEventNames.TOOL_SELECTED)
                def tool_selected(agent, tool_message):
                    if not args.quiet:
                        if (
                            tool_message.tool_arguments
                            and "thought" in tool_message.tool_arguments
                        ):
                            message = f"Using tool {tool_message.tool_name}: {tool_message.tool_arguments['thought']}"
                        else:
                            message = f"Using tool {tool_message.tool_name}..."
                        cprint(message, "green")

                cprint("******************ENTERING CHAT******************", "white")
                cprint(
                    "You are entering a chat with BondAI...\nYou can exit any time by typing 'exit'.",
                    "white",
                )
                intro_message = "The user has just logged in. Please introduce yourself in a friendly manner."
                group_conversation.send_message(
                    recipient_name=user_liaison_profile.NAME,
                    message=intro_message,
                )
            except KeyboardInterrupt:
                cprint(f"\n\nStopping BondAI CLI...\n", "red")

    except BudgetExceededException as e:
        cprint(
            f"\n\nThe budget for this task has been exceeded and will stop.\n", "red"
        )
