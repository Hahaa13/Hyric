from aiohttp import ClientSession, CookieJar
from twocaptcha import TwoCaptcha

class CaptchaSolverNormal:
    def __init__(self, captcha_url: str, configs: dict, logger) -> None:
        self.captcha_url = captcha_url
        self.configs = configs
        self.logger = logger
        self.solver_name = None
        self.solver = None
        self.result = None
        self.work = False
    
    def solve(self, minlen: int, maxlen: int, numeric: int = 4, case: bool = True) -> None:
        for captcha_solver in self.configs["captcha_solvers"]:
            if captcha_solver["enable"]:
                if captcha_solver["name"] == "2captcha":
                    try:
                        self.solver = TwoCaptcha(captcha_solver["api_key"])
                        self.result = self.solver.normal(self.captcha_url, minlen=minlen, maxlen=maxlen, numeric=numeric, case=case)
                        self.work = True
                    except Exception as e:
                        self.logger.error(f"CAPTCHA SOLVER ERROR: {e}")
                self.solver_name = captcha_solver["name"]
                break

    def getresult(self) -> str:
        if self.solver_name == "2captcha":
            return self.result["code"]
    
    def report(self, check: bool) -> None:
        if self.solver_name == "2captcha":
            self.solver.report(self.result["captchaId"], check)

class HCaptchaSolver:
    def __init__(self, configs: dict, logger, sitekey: str, url: str) -> None:
        self.configs = configs
        self.logger = logger
        self.sitekey = sitekey
        self.url = url
        self.solver_name = None
        self.result = None
        self.work = False
    
    def solver(self) -> None:
        for captcha_solver in self.configs["captcha_solvers"]:
            if captcha_solver["enable"]:
                if captcha_solver["name"] == "2captcha":
                    try:
                        solver = TwoCaptcha(captcha_solver["api_key"])
                        self.result = solver.hcaptcha(self.sitekey, self.url)
                        self.work = True
                    except Exception as e:
                        self.logger.error(f"CAPTCHA SOLVER ERROR: {e}")
                self.solver_name = captcha_solver["name"]
                break
    
    def getresult(self):
        if self.solver_name == "2captcha":
            return self.result["code"]