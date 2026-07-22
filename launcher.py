"""Streamlit app launcher for PyInstaller packaging."""
import sys
import os
from streamlit.web import cli as stcli

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(base_dir, "main.py")
    sys.argv = ["streamlit", "run", target, "--global.developmentMode=false"]
    sys.exit(stcli.main())