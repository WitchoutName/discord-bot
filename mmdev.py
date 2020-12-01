from discord import *
from discord.utils import get
from discord.ext import commands
import random
import aiohttp
from io import BytesIO
from Dev.Classes.Restdb import *
from Dev.Classes.CommandMannager import *


#token = "".join([f'{x.replace("\n", "")}.' for x in open("token.txt", "r")])            heeeeeeeere
#print(token)
base_url = "https://discordmmdev-4192.restdb.io/rest"
headers = {
    'content-type': "application/json",
    'x-apikey': "a80deec3bdf880ed69e92e8dfe780301f2db6",
    'cache-control': "no-cache"
}

db = Restdb(base_url=base_url, headers=headers)
client = commands.Bot(command_prefix = 'pls ', intents=Intents.all())
CommandMannager.init(client, db)

async def update_request(payload, check_full):
    channel, message = await MmRequest.get_message(message_id=str(payload.message_id), channel_id=str(payload.channel_id))
    request = db.get_request(by="message_id", value=str(message.id))
    if request:
        count = [x for x in [x.strip() for x in message.embeds[0].fields[1].name.partition("/")] if x != "/"]
        if count[0] < count[1] or check_full:
            await MmRequest.update(request=request)


async def filter_requests(**kwargs):
    y = 0
    for request in db.requests:
        channel, message = await MmRequest.get_message(message_id=request["message_id"], channel_id=request["channel_id"])
        if not channel or not message:
            db.remove_request(request["message_id"])
            db.log(f"Deleting empty request {request['message_id']}.")
            y += 1
    if y > 0:
        if "ctx" in kwargs:
            await kwargs["ctx"].send(f"{y} empty requests Deleted!")


async def autorized(ctx, **kwargs):
    if "admins" in db.get_guild(ctx.guild.id):
        ad = db.get_guild(ctx.guild.id)["admins"]
        admins = []
        [admins.extend(ad[x]) for x in ad]
        for admin in admins:
            if int(admin) in [x.id for x in ctx.author.roles] or int(admin) == ctx.author.id:
                db.log("User autorized.")
                return True
    if ctx.author.id == ctx.guild.owner_id:
        return True
    if not kwargs["check"] if "check" in kwargs else True:
        await ctx.send(embed=Embed(title="You are not allowed to use this command!", color=Color.red()))
    return False


async def send_url_image(**kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(kwargs["url"]) as resp:
            buffer = BytesIO(await resp.read())

    await kwargs["ctx"].send(file=File(buffer, filename=f"smth.{kwargs['end']}"))


@client.event
async def on_raw_reaction_add(payload):

    await update_request(payload, False)


@client.event
async def on_raw_reaction_remove(payload):
    await update_request(payload, True)


@client.event
async def on_ready():
    print("Bot is ready.")
    await client.change_presence(activity=Game("with his pp"))


@client.event
async def on_guild_join(_guild):
    db.add_guild(str(_guild.id))


@client.event
async def on_guild_remove(_guild):
    db.remove_guild(str(_guild.id))


class Admin(commands.Cog):
    @commands.command(name="fr", brief="Deletes all the empty requests in the database.")
    async def filterrequests(self, ctx):
        await filter_requests(ctx=ctx)

    @commands.command(brief="Deletes given number of messages in this channel.")
    async def delete(self, ctx, num):
        async for x in ctx.channel.history(limit=int(num)):
            await x.delete()

    @commands.command(brief="get/add/remove/set @role @member @role ...")
    async def acces(self, ctx, method, *args):
        methods = ["add", "remove", "set", "get"]
        if await autorized(ctx):
            guild = db.get_guild(str(ctx.guild.id))
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

                        db.update_guild(ctx.guild.id, admins={"roles": roles, "members": members})
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
                        db.update_guild(ctx.guild.id, admins={"roles": roles, "members": members})
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
                        db.update_guild(ctx.guild.id, admins={"roles": roles, "members": members})
                        pvals = [f"<@&{x}>\n" for x in roles]
                        pvals.extend([f"<@{x}>\n" for x in members])
                        embed = Embed(color=Color.green())
                        embed.add_field(name="Admins set to: ", value="".join(pvals)[:-1] if len(pvals) > 0 else "None", inline=True)

                    await ctx.send(embed=embed)

                else:
                    await ctx.send(embed=Embed(title=f"Method \'{method}\' not found!", color=Color.red()))


class Development(commands.Cog):
    @commands.command(brief="Makes me leave the server ;(.")
    async def leave(self, ctx):
        if await client.is_owner(ctx.author):
            await ctx.guild.leave()

    @commands.command(brief="Clears out the \"guild\" section of the database.")
    async def deleteall(self, ctx):
        if await client.is_owner(ctx.author):
            db.remove_guilds()

    @commands.command(brief="Uploads all joined gulid to the database.")
    async def updateguilds(self, ctx):
        count = 0
        for x in client.guilds:
            if str(x.id) not in [x["id"] for x in db.guilds]:
                db.add_guild(str(x.id))
                count += 1
        if count > 0:
            await ctx.send(f"{count} guilds added!")

    @commands.command(brief="Showes all joined guilds.")
    async def getguilds(self, ctx):
        embed=Embed(color=Color.orange())
        embed.add_field(name="Joined guilds: ", value="".join([x.name+"\n" for x in client.guilds]), inline=True)
        await ctx.send(embed=embed)


class User(commands.Cog):
    @commands.command(brief="Check, if you are autorized to use admin commands.")
    async def daddy(self, ctx):
        if await autorized(ctx, check=True):
            await ctx.send(embed=Embed(title="Yeah boiiiiiiiii :white_check_mark:", color=Color.green()))
        else:
            await ctx.send(embed=Embed(title="Ur not old enough :x:", color=Color.red()))

    @commands.command(brief="Express your feeling to somebody. ❤")
    async def fu(self, ctx, member):
        if member.startswith("<@") and member.endswith(">"):
            if "!" in member:
                try:
                    user = await client.fetch_user(member[3:-1])
                except:
                    user = None
                if user:
                    if await client.is_owner(user):
                        await ctx.send(f"Fuck you {ctx.author.mention}, I'm not allowed to insult my master!")
                    elif user.id == client.user.id:
                        await send_url_image(ctx=ctx, url="https://media1.tenor.com/images/b3707f0233956a2dc81b6ece7ecb4aec/tenor.gif", end="gif")
                    else:
                        lines = ["no one likes you!", "I'm deeply disappointed in you!", "you're full of shit!",
                                 "you shouldn't be allowed to be here!",
                                 "yo mamma is so ugly when she tried to join an ugly contest they said, \"Sorry, no professionals.\""]
                        await ctx.send(f"Fuck you {user.mention}, {random.choice(lines)}")
            roles = await ctx.guild.fetch_roles()
            if "&" in member and len([x for x in roles if x.mention == member and client.user.name == x.name]) > 0:
                await send_url_image(ctx=ctx, url="https://media1.tenor.com/images/b3707f0233956a2dc81b6ece7ecb4aec/tenor.gif", end="gif")

    @commands.command()
    async def heh(self, ctx, member):
        print(member, client.user.id)

    @commands.command(brief="@role \"game\" language reaction count-of-looked-for \"some message\"")
    async def mm(self, ctx, *args):
        print(args)
        # group, game, language, reaction, goal, message
        # !mm everyone CSGO en :fire: 4 "bang bang :point_right: :point_right:"

        #async for x in ctx.channel.history(limit=1):
        #    await x.delete()
        lan = args[2].lower()
        embed = Embed(title=MmRequest.lines[lan]["title"].format(ctx.author.display_name, args[4], args[1]),
                      description=MmRequest.lines[lan]["description"].format(ctx.author.mention, args[5]))
        embed.add_field(name=MmRequest.lines[lan]["f1n"], value=MmRequest.lines[lan]["f1v"], inline=True)
        embed.add_field(name=MmRequest.lines[lan]["f2n"].format(0, int(args[4])+1), value=MmRequest.lines[lan]["f2v"].format(int(args[4])+1), inline=True)
        embed.set_footer(text=MmRequest.lines[lan]["footer"].format(args[3]))

        mess = await ctx.send(f"{args[0]}", embed=embed)
        for x in client.cached_messages:
            if x.author == client.user:
                cache_mess = get(client.cached_messages, id=mess.id)
                await cache_mess.add_reaction(args[3])
                request = {
                    "channel_id": str(cache_mess.channel.id),
                    "message_id": str(cache_mess.id),
                    "reaction": args[3],
                    "goal": int(args[4]) + 1,
                    "language": lan
                }
                db.add_request(request)
                db.add_requests_to_guild(guild_id=str(ctx.guild.id), request_ids=[str(cache_mess.id)])

                break


client.add_cog(User())
client.add_cog(Admin())
client.add_cog(Development())

client.run(token)
