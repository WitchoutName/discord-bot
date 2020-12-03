from discord.ext import commands
from Classes.CommandMannager import DsClCon
from Classes.CommandMannager import CommandMannager as cm
from Classes.CommandMannager import MmRequest as mm
from discord import *

class Development(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Makes me leave the server ;(.")
    async def leave(self, ctx):
        if await self.client.is_owner(ctx.author):
            await ctx.guild.leave()

    @commands.command(brief="Clears out the \"guild\" section of the database.")
    async def deleteall(self, ctx):
        if await self.client.is_owner(ctx.author):
            cm.db.remove_guilds()

    @commands.command(brief="Uploads all joined gulid to the database.")
    async def updateguilds(self, ctx):
        count = 0
        for x in self.client.guilds:
            if str(x.id) not in [x["id"] for x in cm.db.guilds]:
                cm.db.add_guild(str(x.id))
                count += 1
        if count > 0:
            await ctx.send(f"{count} guilds added!")

    @commands.command(brief="Showes all joined guilds.")
    async def getguilds(self, ctx):
        embed=Embed(color=Color.orange())
        embed.add_field(name="Joined guilds: ", value="".join([x.name+"\n" for x in self.client.guilds]), inline=True)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Development(client))
