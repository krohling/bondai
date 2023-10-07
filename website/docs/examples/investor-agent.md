---
sidebar_position: 1
---

# Investor Agent

In this example we demonstrate BondAI's ability to use the Alpaca Market APIs to buy and sell stocks. Note that it is highly recommended that you use [Paper Trading](https://alpaca.markets/docs/trading/paper-trading/) for this example.

First we will configure the environment variables for OpenAI and Alpaca Markets.

```bash
export OPENAI_API_KEY=sk-XXXXXXXXXX
export ALPACA_API_KEY=XXXXXXXXXX
export ALPACA_SECRET_KEY=XXXXXXXXXX
```

Next we will create an Agent with 2 tools:
- **CreateOrderTool** allows the Agent to create buy and sell orders.
- **ListPositionsTool** allows the Agent to pull a list of the user's current positions.

```python
from bondai.agent import Agent
from bondai.tools.alpaca_markets import CreateOrderTool, GetAccountTool, ListPositionsTool

task = "Sell off all my current positions and buy 10 shares of Nvidia."

Agent(tools=[
  CreateOrderTool(),
  ListPositionsTool()
]).run(task)
```

## Example Output

```
Using the list_positions tool
Thought: I need to list all the current positions of the user to sell them off.
Arguments
Output: Symbol: NVDA Quantity: 20 Entry Share Price: 452.3545 Current Share Price: 434.99 Unrealized Prof...


Using the create_order tool
Thought: I need to sell all the current positions of the user.
Arguments
side: sell
symbol: NVDA
quantity: 20
order_type: market
time_in_force: day
Output: Order ID: f29631a6-f2ca-4237-8e14-7e1734312a97 Status: OrderStatus.ACCEPTED Filled At: None Symbo...


Using the create_order tool
Thought: I need to buy 10 shares of NVDA as per the user's request.
Arguments
side: buy
symbol: NVDA
quantity: 10
order_type: market
time_in_force: day
Output: Order ID: a48044db-d71a-4ded-bdb1-11d74f8f8ece Status: OrderStatus.ACCEPTED Filled At: None Symbo...


Using the final_answer tool
Arguments
input: All your current positions have been sold and 10 shares of Nvidia (NVDA) have been bought as per ...
Output: All your current positions have been sold and 10 shares of Nvidia (NVDA) have been bought as per ...
```