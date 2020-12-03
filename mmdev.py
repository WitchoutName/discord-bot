from discord import *
from discord.utils import get
from discord.ext import commands
import os
from Classes.Restdb import *
from Classes.CommandMannager import *

file = open("token.txt", "r")
token = "".join([f'{x[:-1]}.' for x in file])[:-1]
file.close()


base_url = "https://discordmmbot-6ea2.restdb.io/rest"
headers = {
    'content-type': "application/json",
    'x-apikey': "6564584f72ceaae820a73a09d35b113904e32",
    'cache-control': "no-cache"
}

db = Restdb(base_url=base_url, headers=headers)
client = commands.Bot(command_prefix = '!', intents=Intents.all())
CommandMannager.init(client, db)



@client.event
async def on_raw_reaction_add(payload):

    await CommandMannager.update_request(CommandMannager, payload, False)


@client.event
async def on_raw_reaction_remove(payload):
    await CommandMannager.update_request(CommandMannager, payload, True)


@client.event
async def on_ready():
    print("Bot is ready.")
    await client.change_presence(activity=Game("with his pp"))


@client.event
async def on_guild_join(_guild):
    db.add_guild(_guild.id)


@client.event
async def on_guild_remove(_guild):
    db.remove_guild(_guild.id)

for file_name in os.listdir("./Classes/Cogs"):
    if file_name.endswith(".py"):
        client.load_extension(f"Classes.Cogs.{file_name[:-3]}")

client.run(token)
