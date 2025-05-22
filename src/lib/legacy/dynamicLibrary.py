import importlib
import inspect
from types import ModuleType
from util.logging import log
from lib.dynamiclibrary.loader import DynamicLibraryLoader as DynamicLibraryLoaderNew
from lib.dynamiclibrary.structs import DynamicLibrary as DynamicLibraryStruct

class DynamicLibrary(DynamicLibraryStruct):
    def __init__(self):
        pass

class DynamicLibraryLoader(DynamicLibraryLoaderNew):
    def __init__(self):
        pass