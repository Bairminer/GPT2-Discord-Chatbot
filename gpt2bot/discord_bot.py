#  Licensed under the MIT license.

import configparser
import argparse
import logging
import random
import asyncio

import discord
from discord.ext import commands
import time
import os
import sys
import re
#import matplotlib as mpl
#mpl.use('Agg')
#import matplotlib.pyplot as plt
import traceback


from model import download_model_folder, download_reverse_model_folder, load_model
from decoder import generate_response


from textblob import TextBlob
from googletrans import Translator




# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = commands.Bot(command_prefix="BOT_NAME")


#tenor_gifs = tenorpy.Tenor()

global translator

global num_samples
global max_turns_history
global model
global tokenizer
global mmi_model
global config
global mmi_tokenizer
global start_time
global history_dict
import datetime

@client.event
async def on_ready():
    global translator
    
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    global history_dict

    if(history_dict is None):
        history_dict = {}
    translator = Translator()
    print('Logged in as '+client.user.name+' (ID:'+str(client.user.id)+') | '+str(len(client.guilds))+' servers | ' + getAllUsersCount())
    await client.change_presence(activity=discord.Game(name='remind me to fix bugs'))
    #schedule.every().day.at("00:00").do(client.loop.call_soon_threadsafe, restart_script())
    #client.loop.create_task(run_schedule())


#Called when a message is received
@client.listen()
async def on_message(message):
    global turn
    global turn2
    global from_index
    global history_dict
    if not (message.author == client.user): #Check to ensure the bot does not respond to its own messages
        if(message.mention_everyone == False):
            if(client.user.mentioned_in(message) or isinstance(message.channel, discord.abc.PrivateChannel)): #Check if the bot is mentioned or if the message is in DMs
                async with message.channel.typing(): #Show that the bot is typing
                    translator = Translator()
                    txtinput = message.content.replace("<@" + str(client.user.id) + ">", "").replace("<@!" + str(client.user.id) + ">", "")  #Filter out the mention so the bot does not get confused
                    blob = TextBlob(txtinput)
                    lang = translator.detect(txtinput).lang
                    #lang = "en"
                    try:
                        if(lang != "en"):
                            txtinput = str(translator.translate(txtinput, dest="en", src=lang).text)
                            #_context.append(txtinput)
                    except:
                        print("A translation error occured")
                    if(isinstance(message.channel, discord.abc.PrivateChannel)):
                            txt = get_response(txtinput, message.author.id, False) #Get a response!
                    else:
                            txt = get_response(txtinput, message.guild.id, False) #Get a response!
                    response_blob = TextBlob(txt)
                    try:
                        bot_message = await message.channel.send(txt) #Fire away!
                    except:
                        txt = traceback.format_exc() #Fetch error
                        txt = "An error has occurred. Please try again:\n```" + txt + "```"
                        bot_message = await message.channel.send(txt)  # Fire away!
                        history_dict = {} #Clear history


def getAllUsersCount():
    guilds = client.guilds
    user_count = 0
    for g in guilds:
         user_count += len(g.members)
    return("Current user count: " + str(user_count))

def run_chat():
    # Parse parameters
    global translator
    
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    global history_dict
    global token
    
    num_samples = config.getint('decoder', 'num_samples')
    max_turns_history = config.getint('decoder', 'max_turns_history')

    logger.info("Running the chatbot...")
    turns = []
    loop = asyncio.get_event_loop()
    task1 = loop.create_task(client.start(token))
    gathered = asyncio.gather(task1, loop=loop)
    loop.run_until_complete(gathered)
    
  
  
def get_prescripted_lines(filepath):
    lines = []
    with open(filepath, "r") as f:
        for line in f:
            lines.append(line)
    return lines
global static_history
static_history = get_prescripted_lines("./constant_thoughts.txt")
def get_response(prompt, channel_id, do_infinite):
    global translator
    global turn
    global turn2
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    global history_dict
    global from_index
    if max_turns_history == 0:
        # If you still get different responses then set seed
        turns = []

    # A single turn is a group of user messages and bot responses right after
    turn = {
        'user_messages': [],
        'bot_messages': []
    }
    str_channel_id = str(channel_id)    
    #turns.append(turn)
    turn['user_messages'].append(prompt)
    if not channel_id in history_dict:
        history_dict[channel_id] = []
    
    
    history_dict[channel_id].append(turn)
    # Merge turns into a single history (don't forget EOS token)
    history = ""
    from_index = max(len(history_dict[channel_id])-max_turns_history-1, 0) if max_turns_history >= 0 else 0
    for message in static_history:
        history += message + tokenizer.eos_token
    for i in range(len(history_dict[channel_id])):
        if(i >= from_index):
            turn2 = history_dict[channel_id][i]
        else:
            continue
        # Each turn begings with user messages
        for message in turn2['user_messages']:
            history += message + tokenizer.eos_token
        for message in turn2['bot_messages']:
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
    #print(history_dict)
    return bot_message

def main():
    global translator
    
    global num_samples
    global max_turns_history
    global model
    global tokenizer
    global mmi_model
    global mmi_tokenizer
    global config
    global history_dict
    global token

    token = "YOUR_TOKEN_HERE" # Replace TOKEN_GOES_HERE with your discord API bot token!
    history_dict = {}
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
    

