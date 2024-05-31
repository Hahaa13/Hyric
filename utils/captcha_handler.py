from twocaptcha import TwoCaptcha
from utils.bot import Bot

class CaptchaSolverNormal:
    def __init__(self, captcha_url: str, bot: Bot, minlen: int, maxlen: int, numeric: int = 4, case: bool = True) -> None:
        self.configs = bot.configs
        self.solver_name = ""
        self.work = False
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
