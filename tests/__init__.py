import sys
from pathlib import Path

# Ensure the src directory is on the path so tests can import the package
SRC_PATH = Path(__file__).resolve().parents[1] / 'src'
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
import types
if 'streamlit' not in sys.modules:
    st_stub = types.ModuleType('streamlit')
    st_stub.tabs = lambda *args, **kwargs: []
    st_stub.subheader = lambda *args, **kwargs: None
    st_stub.write = lambda *args, **kwargs: None
    st_stub.altair_chart = lambda *args, **kwargs: None
    st_stub.error = lambda *args, **kwargs: None
    sys.modules['streamlit'] = st_stub
