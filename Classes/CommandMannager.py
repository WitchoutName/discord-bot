class CommandMannager:
    client, db = None, None
    @staticmethod
    def init(_client, _db):
        CommandMannager.client, CommandMannager.db = _client, _db

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
    async def update(**kwargs):
        if "request" in kwargs:
            db_request = kwargs["request"]
        else:
            return -1

        added, users = [], []
        channel, message = await MmRequest.get_message(message_id=str(db_request["message_id"]), channel_id=str(db_request["channel_id"]))

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
