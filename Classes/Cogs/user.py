from discord.ext import commands
from discord.utils import get
from discord import *
from Classes.CommandMannager import DsClCon
from Classes.CommandMannager import CommandMannager as cm
from Classes.CommandMannager import MmRequest as mm
from emoji import UNICODE_EMOJI
import random

class User(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief="Check, if you are autorized to use admin commands.")
    async def daddy(self, ctx):
        if await cm.autorized(ctx):
            await ctx.send(embed=Embed(title="Yeah boiiiiiiiii :white_check_mark:", color=Color.green()))
        else:
            await ctx.send(embed=Embed(title="Ur not old enough :x:", color=Color.red()))

    @commands.command(brief="Express your feeling to somebody. ❤")
    async def fu(self, ctx, member):
        if member.startswith("<@") and member.endswith(">"):
            if "!" in member:
                try:
                    user = await self.client.fetch_user(member[3:-1])
                except:
                    user = None
                if user:
                    if await self.client.is_owner(user):
                        await ctx.send(f"Fuck you {ctx.author.mention}, I'm not allowed to insult my master!")
                    elif user.id == self.client.user.id:
                        await cm.send_url_image(ctx=ctx, url="https://media1.tenor.com/images/b3707f0233956a2dc81b6ece7ecb4aec/tenor.gif", end="gif")
                    else:
                        lines = ["no one likes you!", "I'm deeply disappointed in you!", "you're full of shit!",
                                 "you shouldn't be allowed to be here!",
                                 "yo mamma is so ugly when she tried to join an ugly contest they said, \"Sorry, no professionals.\""]
                        await ctx.send(f"Fuck you {user.mention}, {random.choice(lines)}")
            roles = await ctx.guild.fetch_roles()
            if "&" in member and len([x for x in roles if x.mention == member and self.client.user.name == x.name]) > 0:
                await cm.send_url_image(ctx=ctx, url="https://media1.tenor.com/images/b3707f0233956a2dc81b6ece7ecb4aec/tenor.gif", end="gif")

    @commands.command()
    async def heh(self, ctx, member):
        print([x for x in member if x in UNICODE_EMOJI])

    @commands.command(brief="@role @member @mem... game name :reaction: count-of-looked-for some message")
    async def mm(self, ctx, *args):
        mentions, game_name, mess, count = [], "", "", 0
        for arg in args:
            if await DsClCon.get_user(ctx, arg) or await DsClCon.get_role(ctx, arg):
                mentions.append(arg)
                count += 1
            else:
                break

        for arg in args[count:]:
            if arg not in UNICODE_EMOJI:
                game_name += " "+arg
                count += 1
            else:
                reaction = arg
                break

        loook = args[count+1]
        for arg in args[count+2:]:
            mess += " "+arg

        mess, game_name, mentions = mess[1:], game_name[1:], "".join([x+" " for x in mentions])[:-1]

        lan = cm.db.get_guild(ctx.guild.id)["language"]
        embed = Embed(title=mm.lines[lan]["title"].format(ctx.author.display_name, loook, game_name),
                      description=mm.lines[lan]["description"].format(ctx.author.mention, mess))
        embed.add_field(name=mm.lines[lan]["f1n"], value=mm.lines[lan]["f1v"], inline=True)
        embed.add_field(name=mm.lines[lan]["f2n"].format(0, int(loook)+1), value=mm.lines[lan]["f2v"].format(int(loook)+1), inline=True)
        embed.set_footer(text=mm.lines[lan]["footer"].format(reaction))

        mess = await ctx.send(f"{mentions}", embed=embed)
        for x in self.client.cached_messages:
            if x.author == self.client.user:
                cache_mess = get(self.client.cached_messages, id=mess.id)
                await cache_mess.add_reaction(reaction)
                request = {
                    "channel_id": str(cache_mess.channel.id),
                    "message_id": str(cache_mess.id),
                    "reaction": reaction,
                    "goal": int(loook) + 1,
                    "language": lan
                }
                cm.db.add_request(request)
                cm.db.add_requests_to_guild(guild_id=str(ctx.guild.id), request_ids=[str(cache_mess.id)])
                break


def setup(client):
    client.add_cog(User(client))
