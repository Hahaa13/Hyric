from aiohttp import ClientSession, CookieJar
from twocaptcha import TwoCaptcha

class CaptchaSolverNormal:
    def __init__(self, captcha_url: str, configs: dict) -> None:
        self.configs = configs
        self.solver_name = ""
        self.work = False
    
    def solver(minlen: int, maxlen: int, numeric: int = 4, case: bool = True) -> None:
        for captcha_solver in self.configs["captcha_solvers"]:
            if captcha_solver["enable"]:
                if captcha_solver["name"] == "2captcha":
                    try:
                        self.solver = TwoCaptcha(captcha_solver["api_key"])
                        self.result = self.solver.normal(captcha_url, minlen=minlen, maxlen=maxlen, numeric=numeric, case=case)
                        self.work = True
                    except Exception as e:
                        bot.logger.error(f"CAPTCHA SOLVER ERROR: {e}")
                self.solver_name = captcha_solver["name"]
                break

    def getresult(self) -> str:
        if self.solver_name == "2captcha":
            return self.result["code"]
    
    def report(self, check: bool) -> None:
        if self.solver_name == "2captcha":
            self.solver.report(self.result["captchaId"], check)

class HCaptchaSolver:
    def __init__ (self, url: str, host: str, url_api_verify: str, configs: dict, sitekey: str, oauth: str, logger) -> None:
        self.url = url
        self.host = host
        self.url_api_verify = url_api_verify
        self.configs = configs
        self.sitekey = sitekey
        self.oauth = oauth
        self.logger = logger
        self.token = configs["token"]
    
    async def solver(self) -> bool:
        for captcha_solver in self.configs["captcha_solvers"]:
            if captcha_solver["enable"]:
                if captcha_solver["name"] == "2captcha":
                    try:
                        solver = TwoCaptcha(captcha_solver["api_key"])
                        result = solver.hcaptcha(sitekey=self.sitekey,url=self.url)["code"]
                        break
                    except Exception as e:
                        self.logger.error(f"CAPTCHA SOLVED ERROR: {e}")
        else:
            self.logger.warning("CAPTCHA NOT SOLVED BECAUSE NO ENABLE API SOLVED")
            return False
        headers = {"Accept": "application/json, text/plain, */*","Accept-Encoding": "gzip, deflate, br","Accept-Language": "en-US;en;q=0.8","Content-Type": "application/json;charset=UTF-8","Origin": self.host,"Referer": self.url,'Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin',"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
        try:
            async with (await self._get_oauth()) as session:
                cookies = {cookie.key: cookie.value for cookie in session.cookie_jar}
                async with session.post(self.url_api_verify,headers=headers,json={"token": result},cookies=cookies) as res:
                    self.logger.info(f"LINK CAPTCHA SOLVED - {res.status}")
                    return True
        except Exception as e:
            self.logger.error(e)
            return False

    async def _get_oauth(self):
        async with ClientSession() as session:
            payload = {"permissions": "0","authorize": True}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0','Accept': '*/*','Accept-Language': 'en-US,en;q=0.5','Accept-Encoding': 'gzip, deflate, br','Content-Type': 'application/json','Authorization': self.token,'X-Super-Properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRmlyZWZveCIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJlbi1VUyIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQ7IHJ2OjEwOS4wKSBHZWNrby8yMDEwMDEwMSBGaXJlZm94LzExMS4wIiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTExLjAiLCJvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6IiIsInJlZmVycmluZ19kb21haW4iOiIiLCJyZWZlcnJlcl9jdXJyZW50IjoiIiwicmVmZXJyaW5nX2RvbWFpbl9jdXJyZW50IjoiIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTg3NTk5LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==','X-Debug-Options': 'bugReporterEnabled','Origin': 'https://discord.com','Connection': 'keep-alive','Referer': self.oauth.replace("/api/v9", ""),'Sec-Fetch-Dest': 'empty','Sec-Fetch-Mode': 'cors','Sec-Fetch-Site': 'same-origin','TE': 'trailers',}
            async with session.post(self.oauth, headers=headers, json=payload) as res:
                if res.status == 401:
                    self.logger.warning("INVALID TOKEN")
                elif res.status == 200:
                    result_session = await self._submit_oauth(res)
                    return result_session
                else:
                    self.logger.error(await res.text())

    async def _submit_oauth(self, res):
        response = await res.json()
        locauri = response.get("location")
        headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.5", "connection": "keep-alive","host": self.host.replace("/","").replace("https:",""),"referer": "https://discord.com/", "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "cross-site", "sec-fetch-user": "?1", "upgrade-insecure-requests": "1", "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0"}
        async with ClientSession(cookie_jar=CookieJar()) as session:
            async with session.get(locauri, headers=headers, allow_redirects=False) as res2:
                if res2.status in (302, 307):
                    self.logger.info("TOKEN ADDED TO OAUTH")
                    return session
                else:
                    self.logger.warning(f"FAILED TO ADDED TOKEN TO OAUTH | {res2.status}")
                    return

    