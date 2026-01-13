import pathlib
import sb

class Path:
    root = pathlib.Path.cwd()
    pref_config = root / "sb" / "pref_config.toml"
    output = root / "output"
    downloads = output / "download"

class Content:
    pref_config = sb.read(Path.pref_config, mode='rb')
