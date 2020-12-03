from discord import *
import aiohttp
from io import BytesIO


class CommandMannager:
    client, db = None, None
    lines = {"en": ["Language changed to english.", f"Language unknown."],
             "pl": ["Zmiana języka na polski.", "Nieznany język."],
             "cz": ["Jazyk změněn na češtinu.", "Neznámý jazyk."]}


    @staticmethod
    def init(_client, _db):
        CommandMannager.client, CommandMannager.db = _client, _db

    async def autorized(self, ctx, **kwargs):
        if "admins" in CommandMannager.db.get_guild(ctx.guild.id):
            ad = CommandMannager.db.get_guild(ctx.guild.id)["admins"]
            admins = []
            [admins.extend(ad[x]) for x in ad]
            for admin in admins:
                if int(admin) in [x.id for x in ctx.author.roles] or int(admin) == ctx.author.id:
                    CommandMannager.db.log("User autorized.")
                    return True
        if ctx.author.id == ctx.guild.owner_id:
            return True
        if not kwargs["logs"] if "logs" in kwargs else True:
            await ctx.send(embed=Embed(title="You are not allowed to use this command!", color=Color.red()))
        return False

    async def send_url_image(self, **kwargs):
        async with aiohttp.ClientSession() as session:
            async with session.get(kwargs["url"]) as resp:
                buffer = BytesIO(await resp.read())

        await kwargs["ctx"].send(file=File(buffer, filename=f"smth.{kwargs['end']}"))

    async def update_request(self, payload, check_full):
        channel, message = await DsClCon.get_message(message_id=str(payload.message_id),
                                                     channel_id=str(payload.channel_id))
        request = CommandMannager.db.get_request(by="message_id", value=str(message.id))
        if request:
            count = [x for x in [x.strip() for x in message.embeds[0].fields[1].name.partition("/")] if x != "/"]
            if count[0] < count[1] or check_full:
                await MmRequest.update(request=request)


class DsClCon:
    @staticmethod
    async def get_message(**kwargs):
        try:
            chanel = await CommandMannager.client.fetch_channel(int(kwargs["channel_id"]))
        except:
            chanel = None
        try:
            message = await chanel.fetch_message(int(kwargs["message_id"]))
        except:
            message = None
        return [chanel, message]

    @staticmethod
    async def get_user(ctx, member):
        try:
            if isinstance(member, str) and "!" in member:
                user = await CommandMannager.client.fetch_user(member[3:-1])
            elif isinstance(member, int):
                user = await CommandMannager.client.fetch_user(member)
            else:
                user = None
        except:
            user = None
        return user

    @staticmethod
    async def get_role(ctx, role):
        try:
            if isinstance(role, str) and "&" in role:
                group = [x for x in await ctx.guild.fetch_roles() if x.id == int(role[3:-1])]
            elif isinstance(role, int):
                group = [x for x in await ctx.guild.fetch_roles() if x.id == role]
            else:
                group = None
        except:
            group = None
        return group


class MmRequest:
    lines = {
        "en": {
            "title": "{0} is looking for {1} people to play {2}",
            "description": "{0}: {1}",
            "f1n": "Joined:",
            "f1v": "None",
            "f2n": "{0} / {1}",
            "f2v": "{0} more to go!",
            "footer": "React {0} to join!"
        },
        "cz": {
            "title": "{0} hledá {1} lidi na hraní {2}",
            "description": "{0}: {1}",
            "f1n": "Připojeni:",
            "f1v": "Nikdo",
            "f2n": "{0} / {1}",
            "f2v": "Ještě {0}!",
            "footer": "Dej {0}, aby ses přidal!"
        },
        "pl": {
            "title": "{0} szuka {1} osób do gry w {2}",
            "description": "{0}: {1}",
            "f1n": "Dołączył:",
            "f1v": "Nikt",
            "f2n": "{0} / {1}",
            "f2v": "Jeszcze {0}!",
            "footer": "Zarejestruj się {0}, aby dołączyć!"
        }
    }

    @staticmethod
    async def update(**kwargs):
        if "request" in kwargs:
            db_request = kwargs["request"]
        else:
            return -1

        added, users = [], []
        channel, message = await DsClCon.get_message(message_id=str(db_request["message_id"]), channel_id=str(db_request["channel_id"]))

        reaction = [x for x in message.reactions if x.emoji == db_request["reaction"]]
        if len(reaction) > 0:
            async for user in reaction[0].users():
                users.append(user)
            if len(users) > 1:
                await message.remove_reaction(reaction[0].emoji, CommandMannager.client.user)
            elif len(users) < 1:
                await message.add_reaction(reaction[0].emoji)
            added = [user for user in users if user != CommandMannager.client.user]
        else:
            await message.add_reaction(db_request["reaction"])

        message.embeds[0].set_field_at(0, name=message.embeds[0].fields[0].name, value="".join([f"{p.mention}\n" for p in added]) if len(added) > 0 else "None")
        message.embeds[0].set_field_at(1, name=MmRequest.lines[db_request["language"]]["f2n"].format(len(added), db_request['goal']), value=MmRequest.lines[db_request["language"]]["f2v"].format(db_request['goal'] - len(added)))
        await message.edit(embed=message.embeds[0])
