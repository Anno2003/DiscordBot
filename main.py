import os
import discord
import chatbot
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
PREFIX= os.getenv('PREFIX')


helpCmd=commands.DefaultHelpCommand(no_category="Other stuff")
client = commands.Bot(command_prefix=PREFIX,help_command=helpCmd)

chatbot = chatbot.Chatbot()
chatbot.loadIntents("./intents.json")
#TODO: find a way to train only when intents json is changed
chatbot.trainModel()
#chatbot.loadModel()#dont forget to train model if intents.json is changed

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
            response = chatbot.response(message.content)
            await message.channel.send(response)

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