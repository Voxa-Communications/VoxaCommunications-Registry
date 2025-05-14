import inspect
import logging
import os
from colorama import init, Fore, Style, Back
from util.printColor import print_color

class log:
    def __init__(self):
        Caller_Frame = inspect.stack()[1]
        Caller_Module = inspect.getmodule(Caller_Frame[0])
        self.Module_Name = Caller_Module.__name__ if Caller_Module else "__main__"
        self.Logger = logging.getLogger(self.Module_Name)
        self.Logger.setLevel(logging.DEBUG)

    def info(self, message: str) -> None:
        self.Logger.info(f"{message}")
        print_color(f"[INFO]: {message}", Fore.WHITE)

    def error(self, message: str) -> None:
        self.Logger.error(f"{message}")
        print_color(f"[ERROR]: {message}", Fore.RED)