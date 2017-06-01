import importlib
import glob
import os.path

modules = glob.glob(os.path.dirname(__file__)+"/*.py")
__all__ = [ os.path.basename(f)[:-3] for f in modules if os.path.isfile(f) and not f.endswith('__init__.py')]

for corpus in __all__:
    module_settings = importlib.import_module('settings_viewer.'+corpus)