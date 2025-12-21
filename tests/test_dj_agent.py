import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "apps"
    / "backend"
    / "EchoDJ"
    / "dj_agent.py"
)
spec = importlib.util.spec_from_file_location("dj_agent", MODULE_PATH)
dj_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dj_agent)


def test_ensure_download_directory_exists(tmp_path):
    app = dj_agent.AIDJApp.__new__(dj_agent.AIDJApp)
    app.update_status = lambda message: None
    target = tmp_path / "downloads"
    app.ensure_download_directory_exists(target)
    assert target.exists() and target.is_dir()
