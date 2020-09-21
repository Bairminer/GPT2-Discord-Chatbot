# Discord GPT2 Chatbot
Based off of: https://github.com/DoktorHolmes/Maxwell and https://github.com/polakowo/gpt2bot  
Fixed issues with long messages causing the original Maxwell bot to freeze (clears history if an error occurs and prints traceback in Discord), fixed issues with translation causing no response from bot due to misread language, removed statistics reporting which had errors that prevented the original program from running.
## Installation
Please ignore instructions from original readmes  
1. Clone this repository  
2. Install Python 3.7.9 if not installed  
3. Install required libraries (I reccomend using a virtual environment or an IDE like PyCharm). You can install all requirements with "pip install -r requirements.txt":  
requests~=2.24.0  
torch~=1.2.0+cu92  
tqdm~=4.48.2  
transformers~=2.3.0  
python-telegram-bot~=12.8  
numpy~=1.19.1  
discord~=1.0.1  
textblob~=0.15.3  
googletrans~=3.0.0  
matplotlib 2.0.2~=3.3.1
4. Open the folder "gpt2bot"  
5. In discord_bot.py, at line 117, replace "TOKEN_GOES_HERE" with your discord bot's API token  
6. Run discord_bot.py. The model will download automatically.

# Maxwell - A DialoGPT variant for discord.py - Original Readme

Maxwell is my experiment with Microsoft's DialoGPT model and OpenAI's GPT-2 language model, for use on any discord server.  I am planning on fine-tuning much more in the future but for now DialoGPT's model performs admirably.
As of 3-2-2020 I am running this model on my old bot, Maple, which you can invite here:
<a href="https://discordbotlist.com/bots/571924469661302814">
    <img
        width="380"
        height="140"
        src="https://discordbotlist.com/bots/571924469661302814/widget"
        alt="Lithium stats on Discord Bot List">
</a>

## Setup

The recommended python version is 3.6.8.  

### Requirements
You can install all requirements with "pip install -r requirements.txt".

python 3.6.8
numpy 1.16.4
torch 1.2.0
transformers 2.3.0
python-telegram-bot 12.3.0 (Only if you are using the telegram bot)
discord.py 1.2.5
goolgetrans 2.4.0 (For automatic translation with non-english users)
textblob 0.15.3 (Used in some text processing cases)
matplotlib 2.0.2 (Used for modeling statistics)

In discord_bot.py, at line 117, replace "TOKEN_GOES_HERE" with your discord bot's API token.
The model will automatically download and set up upon the first run of the program; you should be good to go!

# gpt2bot - Original Readme

```
User >>> Can we achieve singularity?
Bot >>> What does this mean?
User >>> Can computers become smarter than humans?
Bot >>> Is there any evidence that this is possible?
User >>> It must be doable
Bot >>> But... how?
User >>> I want to find out, that's why I created you
Bot >>> You created me?
User >>> You're my bot
Bot >>> You monster
```

<img src="https://github.com/polakowo/gpt2bot/blob/master/reddit.png?raw=true" width=80>

gpt2bot implements 
  - a decoder ([source](https://github.com/polakowo/gpt2bot/blob/master/gpt2bot/decoder.py)) for [DialoGPT](https://github.com/microsoft/DialoGPT), 
  - an interactive multiturn chatbot ([source](https://github.com/polakowo/gpt2bot/blob/master/gpt2bot/interactive_bot.py)), and 
  - a Telegram chatbot ([source](https://github.com/polakowo/gpt2bot/blob/master/gpt2bot/telegram_bot.py)).
  
The bot is built around [DialoGPT](https://github.com/microsoft/DialoGPT) - a large-scale pretrained dialogue response generation model trained by Microsoft, which was trained on 147M multi-turn dialogue from Reddit discussion thread. The human evaluation results indicate that its quility is comparable to human response quality under a single-turn conversation Turing test.

Since even with properly filtered Reddit dataset the model can generate toxic/inappropriate responses, the Microsoft team was unable to provide the decoding script. This repository implements the decoding script inspired by `run_generation.py` released earlier by Hugging Face. Moreover, it implements a Telegram bot that can be deployed locally, remotely, and even on Colab, and just makes testing fun.
  
## How to use?

### 1. Create a Telegram bot

- Register a new Telegram bot via BotFather (see https://core.telegram.org/bots)

### 2. Deploy the bot

#### Google Colab

[A Colab interactive notebook](https://colab.research.google.com/github/polakowo/gpt2bot/blob/master/Demo.ipynb)

A good thing about Google Colab is free GPU. So why not running the Telegram bot there, for blazingly fast chat? Run the notebook at daytime and do not forget to stop it at night.

#### Docker

- Clone the repository
- Set your parameters such as API token in dialog.cfg
- To avoid re-downloading model files at each re-deployment, download the model files beforehand with
```
# cd gpt2bot/gpt2bot
python model.py
```
- Finally, deploy the container from the root folder
```
docker build -t gpt2bot . && docker run gpt2bot
```

#### Manually

- Clone the repository
- Set your parameters such as API token in dialog.cfg
- Install packages listed in requirements.txt
- Run the script
```
# cd gpt2bot/gpt2bot
python telegram_bot.py
```
- To test the things out in the console, run
```
python interactive_bot.py
```

### 3. Start chatting!

![](telegram_bot.gif)

Just start texting. Append @gif for the bot to generate a GIF instead of text. To reset, type "Bye".

## Updates

#### 18/01/2020

- EOS token is being checked during generation -> gpt2bot is now fast enough to be run on CPU.
- Add support for maximum mutual information (MMI) -> more quality, but slower.

## References

- [Official DialoGPT implementation](https://github.com/microsoft/DialoGPT) and [DialoGPT paper](https://arxiv.org/abs/1911.00536)
- [Thread on current decoding scripts](https://github.com/microsoft/DialoGPT/issues/3)

You can wait for a full DialoGPT release and then replace the decoder.
