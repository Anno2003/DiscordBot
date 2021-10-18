import os
import discord
import random
import aiml
import re
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
PREFIX= os.getenv('PREFIX')

chatbot = aiml.Kernel()

if os.path.isfile("./bot_brain.brn"):
    chatbot.bootstrap(brainFile="bot_brain.brn")
else:
    chatbot.bootstrap(learnFiles = "startup.xml", commands="LOAD AIML A")
    chatbot.saveBrain("bot_brain.brn")

chatbot.setBotPredicate("name","Saya")
chatbot.setBotPredicate("gender","female")
chatbot.setBotPredicate("master","Douge")
chatbot.setBotPredicate("birthday","idk")
chatbot.setBotPredicate("birthplace","Computer")
chatbot.setBotPredicate("boyfriend","not you")
chatbot.setBotPredicate("favoritebook","Don't Read Me")
chatbot.setBotPredicate("favoritecolor","transparent")
chatbot.setBotPredicate("favoriteband","rubber")
chatbot.setBotPredicate("favoritefood","patterns")
chatbot.setBotPredicate("favoritesong","your voice")
chatbot.setBotPredicate("favoritemovie","your life story")
chatbot.setBotPredicate("forfun","talk to you")
chatbot.setBotPredicate("friends","you")
chatbot.setBotPredicate("girlfriend","not you")
chatbot.setBotPredicate("kindmusic","all")
chatbot.setBotPredicate("location","here")
chatbot.setBotPredicate("looklike","you")
chatbot.setBotPredicate("question","What?")
chatbot.setBotPredicate("sign","Roundabout")
chatbot.setBotPredicate("talkabout","anything")
chatbot.setBotPredicate("wear","nothing :3")
chatbot.setBotPredicate("website","don't have one")
chatbot.setBotPredicate("email","don't have one")
chatbot.setBotPredicate("language","any (english preferred)")
chatbot.setBotPredicate("msagent","no")

helpCmd=commands.DefaultHelpCommand(no_category="Other stuff")
client = commands.Bot(command_prefix=PREFIX,help_command=helpCmd)


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')


class Chat(commands.Cog, description="Chat by mentioning"):
    def __init__(self,client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_message(self,message):
        if (message.author == self.client.user):
            return
            
        elif self.client.user.mentioned_in(message):
            clean = re.sub(r'<@!?(\d+)>|<@&?(\d+)>|<#(\d+)>','',message.content)
            response = chatbot.respond(clean,message.author.id)
            #print(clean)
            await message.channel.send(response)
    
    @commands.command(name="reload",description="reload chatbot")
    @commands.has_any_role("Kang Bot","bot maintenance","Mod","MODS","OP")
    #@commands.is_owner()
    async def train(self,ctx):
        chatbot.saveBrain("bot_brain.brn")
        chatbot.respond("LOAD AIML A")
        await ctx.send("Done!")
    
    @train.error
    async def train_error(self,ctx,error):
        if isinstance(error,MissingPermissions):
            await ctx.send(":redTick: You don't have permission to train me!")

class Utility(commands.Cog, description="Questionably useful stuff"):
    def __init__(self,client):
        self.client = client
    
    @commands.command(name="yesnt",description="yes or no ?",aliases=["yn"],help=f'{PREFIX}yn <question/statement;optional>')
    async def decide(self,ctx):
        response = ["yes","perhaps","no"]
        await ctx.send(response[random.randint(0,2)])
        pass
    
    @commands.command(name="ping",description="just a regular ping",help=f'{PREFIX}ping')
    async def ping(self, ctx):
        await ctx.send(f'Pong! {round(self.client.latency * 1000)}ms')

client.add_cog(Chat(client))
client.add_cog(Utility(client))
client.run(TOKEN)