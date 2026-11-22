import runpy
from pathlib import Path

# SafeHands AI main entry point
app_file = Path(__file__).with_name("app.py")

runpy.run_path(str(app_file))