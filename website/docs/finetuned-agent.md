---
sidebar_position: 9
---

# Finetuned Local LLM

The holy grail is to have a capable Agent that can run fully independent of OpenAI and all other 3rd party hosted models. Unfortunately, current open source models make poor Agents. However, we believe that if a robust enough dataset of Agent interactions can be captured, an open source model can be fine tuned, greatly improving it's Agent capabilities.

If you would like to participate and help this cause, simply enable prompt logging while running BondAI which will store all the LLM prompts and responses. Make a PR to this repository adding your prompt logs to the `prompt-dataset` directory. Note that we will make both the dataset and the resulting models available for free on Github and HuggingFace.

Our goal is to get to a dataset of 50K prompts. Let's see what we can do!

**Note: PLEASE make sure that any logs you share are free of personally identifying or sensitive data as they will be shared publically and used to train future models.**