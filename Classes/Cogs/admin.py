from discord.ext import commands
from discord import *
from Classes.CommandMannager import DsClCon
from Classes.CommandMannager import CommandMannager as cm
from Classes.CommandMannager import MmRequest as mm

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="fr", brief="Deletes all the empty requests in the database.")
    async def filterrequests(self, ctx):
        y = 0
        for request in cm.db.requests:
            channel, message = await DsClCon.get_message(message_id=request["message_id"],
                                                         channel_id=request["channel_id"])
            if not channel or not message:
                cm.db.remove_request(request["message_id"])
                cm.db.log(f"Deleting empty request {request['message_id']}.")
                y += 1
        if y > 0:
            await ctx.send(f"{y} empty requests Deleted!")

    @commands.command(brief="Deletes given number of messages in this channel.")
    async def delete(self, ctx, num):
        async for x in ctx.channel.history(limit=int(num)):
            await x.delete()

    @commands.command(brief="Change my language on this server. [cz, en, pl]")
    async def language(self, ctx, ln):
        if await cm.autorized(ctx):
            if ln.lower() in cm.lines:
                cm.db.update_guild(ctx.guild.id, language=ln)
                await ctx.send(embed=Embed(title=f"{cm.lines[ln][0]} :white_check_mark:", color=Color.green()))
            else:
                await ctx.send(embed=Embed(title=f"{cm.lines[cm.db.get_guild(ctx.guild.id)['language']][1]} :woman_shrugging: {''.join([x+', ' for x in CommandMannager.lines])[:-2]}?", color=Color.red()))

    @commands.command(brief="get/add/remove/set @role @member @role ...")
    async def acces(self, ctx, method, *args):
        methods = ["add", "remove", "set", "get"]
        if await cm.autorized(None, ctx):
            guild = cm.db.get_guild(ctx.guild.id)
            if guild:
                if method.lower() in methods:
                    if method == "get":
                        pvals = [f"<@&{x}>\n" for x in guild["admins"]["roles"]]
                        pvals.extend([f"<@{x}>\n" for x in guild["admins"]["members"]])
                        embed = Embed(color=Color.orange())
                        embed.add_field(name="Admins:", value="".join(pvals)[:-1] if len(pvals) > 0 else "None", inline=True)
                    elif method == "set":
                        roles, members = [], []
                        for x in args:
                            if "&" in x and x in [x.mention for x in ctx.guild.roles]:
                                roles.append(x[3:-1])
                            elif "!" in x:
                                if int(x[3:-1]) in [x.id for x in ctx.guild.members]:
                                    members.append(x[3:-1])

                        cm.db.update_guild(ctx.guild.id, admins={"roles": roles, "members": members})
                        embed = Embed(color=Color.green())
                        pvals = [f"<@&{x}>\n" for x in roles]
                        pvals.extend([f"<@{x}>\n" for x in members])
                        embed.add_field(name="Admins set to: ", value="".join(pvals)[:-1] if len(pvals) > 0 else "None",inline=True)
                    elif method == "add":
                        roles, members = [], []
                        for x in args:
                            if "&" in x and x in [x.mention for x in ctx.guild.roles]:
                                if x[3:-1] not in guild["admins"]["roles"]:
                                    roles.append(x[3:-1])
                            elif "!" in x:
                                if int(x[3:-1]) in [x.id for x in ctx.guild.members]:
                                    if x[3:-1] not in guild["admins"]["members"]:
                                        members.append(x[3:-1])
                        roles.extend(guild["admins"]["roles"])
                        members.extend(guild["admins"]["members"])
                        cm.db.update_guild(ctx.guild.id, admins={"roles": roles, "members": members})
                        pvals = [f"<@&{x}>\n" for x in roles]
                        pvals.extend([f"<@{x}>\n" for x in members])
                        embed = Embed(color=Color.green())
                        embed.add_field(name="Admins set to: ", value="".join(pvals)[:-1] if len(pvals) > 0 else "None", inline=True)
                    elif method == "remove":
                        roles, members = guild["admins"]["roles"], guild["admins"]["members"]
                        roles_to_rem, members_to_rem = [], []
                        for x in args:
                            if "&" in x and x in [x.mention for x in ctx.guild.roles]:
                                roles_to_rem.append(x[3:-1])
                            elif "!" in x:
                                if int(x[3:-1]) in [x.id for x in ctx.guild.members]:
                                    members_to_rem.append(x[3:-1])
                        [roles.remove(x) and print(x) for x in roles if x in roles_to_rem]
                        [members.remove(x) and print(x) for x in members if x in members_to_rem]
                        cm.db.update_guild(ctx.guild.id, admins={"roles": roles, "members": members})
                        pvals = [f"<@&{x}>\n" for x in roles]
                        pvals.extend([f"<@{x}>\n" for x in members])
                        embed = Embed(color=Color.green())
                        embed.add_field(name="Admins set to: ", value="".join(pvals)[:-1] if len(pvals) > 0 else "None", inline=True)

                    await ctx.send(embed=embed)

                else:
                    await ctx.send(embed=Embed(title=f"Method \'{method}\' not found!", color=Color.red()))


def setup(client):
    client.add_cog(Admin(client))
