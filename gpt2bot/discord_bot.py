#  Licensed under the MIT license.

import configparser
import argparse
import logging
import random

import discord
import time
import os
import sys
import re
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt


from model import download_model_folder, download_reverse_model_folder, load_model
from decoder import generate_response


from textblob import TextBlob
from googletrans import Translator


global turns

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = discord.Client()

global translator
global turns
global num_samples
global max_turns_history
global model
global tokenizer
global mmi_model
global config
global mmi_tokenizer
import datetime

@client.event
async def on_ready():
    global translator
    global turns
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    translator = Translator()
    print('Logged in as '+client.user.name+' (ID:'+str(client.user.id)+') | '+str(len(client.guilds))+' servers | ' + getAllUsersCount())
    await client.change_presence(activity=discord.Game(name='chat with me!'))


#Called when a message is received
@client.event
async def on_message(message):
    if not (message.author == client.user): #Check to ensure the bot does not respond to its own messages
        if(message.mention_everyone == False):
            if(client.user.mentioned_in(message) or isinstance(message.channel, discord.abc.PrivateChannel)): #Check if the bot is mentioned or if the message is in DMs
                async with message.channel.typing(): #Show that the bot is typing
                    translator = Translator()
                    txtinput = message.content.replace("<@" + str(client.user.id) + ">", "").replace("<@!" + str(client.user.id) + ">", "")  #Filter out the mention so the bot does not get confused
                    if(len(txtinput) > 220): 
                        txt = "I am sorry, that is too long for me."
                    dicestr = re.search("Roll (\d{1,2})d(\d{1,3})",message.content)
                    if(dicestr != None):
                        dice = [dicestr.group(1), dicestr.group(2)]
                        output = "I rolled "
                        for i in range(int(dice[0])):
                            output += str(random.randrange(1, int(dice[1]))) + ", "
                        txt = output
                    else:
                        blob = TextBlob(txtinput)
                        lang = translator.detect(txtinput).lang
                        #lang = "en"
                        if(lang != "en"):
                            txtinput = str(translator.translate(txtinput, dest="en", src=lang).text)
                        #_context.append(txtinput)
                        txt = get_response(txtinput) #Get a response!
                        response_blob = TextBlob(txt)
                        if(lang != "en"):
                            txt = str(translator.translate(txt, dest=lang, src="en").text)
                    bot_message = await message.channel.send(txt) #Fire away!


def getAllUsersCount():
    guilds = client.guilds
    user_count = 0
    for g in guilds:
         user_count += len(g.members)
    return("Current user count: " + str(user_count))


def run_chat():
    # Parse parameters
    global translator
    global turns
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    num_samples = config.getint('decoder', 'num_samples')
    max_turns_history = config.getint('decoder', 'max_turns_history')

    logger.info("Running the chatbot...")
    turns = []
    client.run('TOKEN_GOES_HERE') #Replace TOKEN_GOES_HERE with your bot's discord API token

def get_prescripted_lines(filepath):
    lines = []
    with open(filepath, "r") as f:
        for line in f:
            lines.append(line)
    return lines
global static_history
static_history = get_prescripted_lines("./constant_thoughts.txt")
def get_response(prompt):
    global translator
    global turns
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    global static_history
    if max_turns_history == 0:
        # If you still get different responses then set seed
        turns = []

    # A single turn is a group of user messages and bot responses right after
    turn = {
        'user_messages': [],
        'bot_messages': []
    }
    turns.append(turn)
    turn['user_messages'].append(prompt)
    
    # Merge turns into a single history (don't forget EOS token)
    history = ""
    from_index = max(len(turns)-max_turns_history-1, 0) if max_turns_history >= 0 else 0
    for message in static_history:
        history += message + tokenizer.eos_token
        
    for turn in turns[from_index:]:
        # Each turn begings with user messages
        for message in turn['user_messages']:
            history += message + tokenizer.eos_token
        for message in turn['bot_messages']:
            history += message + tokenizer.eos_token
    
    # Generate bot messages
    bot_messages = generate_response(
        model, 
        tokenizer, 
        history, 
        config, 
        mmi_model=mmi_model, 
        mmi_tokenizer=mmi_tokenizer
    )
    if num_samples == 1:
        bot_message = bot_messages[0]
    else:
        # TODO: Select a message that is the most appropriate given the context
        # This way you can avoid loops
        bot_message = random.choice(bot_messages)
    turn['bot_messages'].append(bot_message)
    return bot_message

def main():
    global translator
    global turns
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    # Script arguments can include path of the config
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--config', type=str, default="chatbot.cfg")
    args = arg_parser.parse_args()

    # Read the config
    config = configparser.ConfigParser(allow_no_value=True)
    with open(args.config) as f:
        config.read_file(f)

    # Download and load main model
    target_folder_name = download_model_folder(config)
    model, tokenizer = load_model(target_folder_name, config)

    # Download and load reverse model
    use_mmi = config.getboolean('model', 'use_mmi')
    if use_mmi:
        mmi_target_folder_name = download_reverse_model_folder(config)
        mmi_model, mmi_tokenizer = load_model(mmi_target_folder_name, config)
    else:
        mmi_model = None
        mmi_tokenizer = None
    
    # Run chatbot with GPT-2
    run_chat()

if __name__ == '__main__':
    main()
 