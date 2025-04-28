import importlib
from util.logging import log

class DynamicLibrary:
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.module = None

    def loadattr(self, attr_name: str):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        try:
            if hasattr(self.module, attr_name):
                return getattr(self.module, attr_name)
            else:
                return None
        except AttributeError as e:
            raise ImportError(f"Attribute {attr_name} not found in module {self.module_name}") from e

    def reload_module(self):
        try:
            self.module = importlib.reload(self.module)
            return self.module
        except ImportError as e:
            raise ImportError(f"Failed to reload module {self.module_name}: {e}")

    def list_attributes(self):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        return dir(self.module)

class DynamicLibraryLoader:
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = log()
        self.logger.info(f"DynamicLibraryLoader Class Initialized with module: {module_name}")
        self.module = None
        
    def load_module(self) -> DynamicLibrary:
        try:
            self.logger.info(f"Loading module: {self.module_name}")
            self.module = importlib.import_module(self.module_name)
            self.logger.info(f"Module {self.module_name} loaded successfully")
            return DynamicLibrary(self.module_name)
        except ImportError as e:
            self.logger.error(f"Error loading module {self.module_name}: {e}")
            raise e

    def unload_module(self):
        try:
            if self.module_name in importlib.sys.modules:
                del importlib.sys.modules[self.module_name]
                self.logger.info(f"Module {self.module_name} unloaded successfully")
            else:
                self.logger.warning(f"Module {self.module_name} is not loaded")
        except Exception as e:
            self.logger.error(f"Error unloading module {self.module_name}: {e}")
            raise e

    def is_module_loaded(self) -> bool:
        return self.module_name in importlib.sys.modules

    def get_module_doc(self):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        return self.module.__doc__

    def get_module_file(self):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        return self.module.__file__

    def execute_function(self, func_name: str, *args, **kwargs):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        try:
            func = getattr(self.module, func_name, None)
            if callable(func):
                self.logger.info(f"Executing function {func_name} from module {self.module_name}")
                return func(*args, **kwargs)
            else:
                raise AttributeError(f"Function {func_name} not found in module {self.module_name}")
        except Exception as e:
            self.logger.error(f"Error executing function {func_name} from module {self.module_name}: {e}")
            raise e

    def list_functions(self):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        return [attr for attr in dir(self.module) if callable(getattr(self.module, attr))]

    def list_classes(self):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        return [attr for attr in dir(self.module) if isinstance(getattr(self.module, attr), type)]

    def get_class(self, class_name: str):
        if self.module is None:
            raise ImportError(f"Module {self.module_name} not loaded")
        try:
            cls = getattr(self.module, class_name, None)
            if isinstance(cls, type):
                return cls
            else:
                raise AttributeError(f"Class {class_name} not found in module {self.module_name}")
        except Exception as e:
            self.logger.error(f"Error retrieving class {class_name} from module {self.module_name}: {e}")
            raise e
