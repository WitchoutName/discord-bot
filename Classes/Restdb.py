import requests as rq
import json
from datetime import datetime as dt


class Restdb:
    def __init__(self, **kwargs):
        self.base_url = kwargs["base_url"]
        self.headers = kwargs["headers"]
        self.guilds = None
        self.requests = []
        self.load_guilds()
        self.load_requests()

    def log(self, string, **kwargs):
        print(str(dt.now()).partition(" ")[2].partition('.')[0]+" |",  "ERROR: "+string if (kwargs["error"] if "error" in kwargs else False) else string)

    def load_guilds(self):
        self.guilds = json.loads(rq.request("GET", self.base_url + "/guild", headers=self.headers).text)
        self.log("Gulids {} loaded!".format("succesfully" if self.guilds else "not"), error=not self.guilds)

    def load_requests(self):
        self.requests = json.loads(rq.request("GET", self.base_url + "/request", headers=self.headers).text)
        self.log("Requests {} loaded!".format("succesfully" if self.requests else "not"), error=not self.requests)

    def get_guild(self, id, **kwargs):
        guild = [x for x in self.guilds if x["id"] == str(id)]
        return guild[0] if len(guild) > 0 else self.log(f"Guild {id} not found.", error=not kwargs["exist"] if "exist" in kwargs else True) and None

    def add_guild(self, id):
        if not self.get_guild(id, exist=True):
            data = json.dumps({"id": str(id), "request": [], "admins": {"roles": [], "members": []}, "language": "en"})
            res = rq.request("POST", f"{self.base_url}/guild", data=data, headers=self.headers)
            self.log(f"Guild {id} added." if res.ok else f"Something went wrong with adding guild {id}!", error=not res.ok)
            if res.ok:
                self.guilds.append(json.loads(res.text))
            return res
        else:
            self.log(f"Guild {id} already exists!", error=True)
            return None

    def update_guild(self, id, **kwargs):
        guild = self.get_guild(id)
        if guild:
            _requests = kwargs["requests"] if "requests" in kwargs else self.get_requests(requests=guild["request"], out="_id")
            _roles = json.dumps(kwargs["admins"]) if "admins" in kwargs else guild["admins"]
            _language = kwargs["language"] if "language" in kwargs else guild["language"]
            data = json.dumps({"id": str(id), "request": _requests, "admins": _roles, "language": _language})
            url = self.base_url+"/guild/"+guild["_id"]
            res = rq.request("PUT", url, data=data, headers=self.headers)
            self.log(f"Guild {id} updated with status {str(res).split()[1][:-1]}.", error=not res.ok)
            if res.ok:
                self.guilds.remove(guild)
                self.guilds.append(json.loads(res.text))

    def remove_guild(self, id):
        guild = self.get_guild(id)
        if guild:
            res = rq.request("DELETE", self.base_url+f"/guild/{guild['_id']}", headers=self.headers)
            if res.ok:
                self.guilds.remove(guild)
            for request in [x["message_id"] for x in guild["request"]]:
                self.remove_request(request)
            return res
        else:
            return None

    def remove_guilds(self):
        for x, guild in enumerate(self.guilds):
            print(self.remove_guild(guild["id"]), guild["id"])
            self.log(f"Guild {guild['id']} has been deleted. ({x+1} / {len(self.guilds)})")
        self.log("Done")

    def get_request(self, **kwargs):
        request = [x for x in self.requests if x[kwargs["by"]] == kwargs["value"]]
        return request[0] if len(request) > 0 else self.log(f"Request {kwargs['value']} not found.", error=True) and None

    def add_request(self, request):
        id = request["message_id"]
        if id not in [x["message_id"] for x in self.requests]:
            data = json.dumps(request)
            res = rq.request("POST", f"{self.base_url}/request", data=data, headers=self.headers)
            self.log(f"Request {id} added." if res.ok else f"Something went wrong with adding request {id}!", error=not res.ok)
            if res.ok:
                self.requests.append(json.loads(res.text))
            return res
        else:
            self.log(f"Request {id} already exists!", error=True)
            return None

    def update_request(self, id, **kwargs):
        request = self.get_request(by="message_id", value=id)
        if request:
            _request = {
                "channel_id": kwargs["channel_id"] if "channel_id" in kwargs else request["channel_id"],
                "message_id": kwargs["message_id"] if "message_id" in kwargs else request["message_id"],
                "reaction": kwargs["reaction"] if "reaction" in kwargs else request["reaction"],
                "goal": kwargs["goal"] if "goal" in kwargs else request["goal"],
            }
            url = self.base_url+"/request/"+request["_id"]
            res = rq.request("PUT", url, data=json.dumps(_request), headers=self.headers)
            self.log(f"Request {id} updated with status {str(res).split()[1][:-1]}.", error=not res.ok)
            if res.ok:
                self.requests.remove(request)
                self.requests.append(json.loads(res.text))

    def remove_request(self, id):
        request = self.get_request(by="message_id", value=id)
        if request:
            res = rq.request("DELETE", self.base_url+f"/request/{request['_id']}", headers=self.headers)
            if res.ok:
                self.requests.remove(request)
            return res
        else:
            return None

    def get_requests(self, **kwargs):
        requests = kwargs["requests"] if "requests" in kwargs else [self.get_request(by=kwargs["by"], value=x) for x in kwargs["values"]]
        return [x[kwargs["out"]] for x in requests] if "out" in kwargs else requests

    def add_requests_to_guild(self, **kwargs):
        guild = self.get_guild(kwargs["guild_id"])
        requests = self.get_requests(requests=guild["request"], out="_id") if len(guild["request"]) > 0 else []
        for request in self.get_requests(by="message_id", values=kwargs["request_ids"], out="_id"):
            if request not in requests:
                requests.append(request)

        self.update_guild(guild["id"], requests=requests)

    def remove_requests_from_guild(self, **kwargs):
        guild = self.get_guild(kwargs["guild_id"])
        requests = self.get_requests(requests=guild["request"], out="_id")
        for request in self.get_requests(by="message_id", values=kwargs["request_ids"], out="_id"):
            if request in requests:
                requests.remove(request)

        self.update_guild(guild["id"], requests=requests)
