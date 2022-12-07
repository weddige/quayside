import logging
import argparse
from pathlib import Path
import yaml

from quayside.cli import add_verbosity_argument, configure_logger
from quayside.app import QuaysideApp

logger = logging.getLogger(__name__)

# Find and load config
for path in [
    Path("./quayside.yaml"),
    Path("~/.quayside.yaml"),
    Path(__file__).parent.joinpath("default.yaml"),
]:
    if path.exists():
        config = path.absolute()
        logger.debug(f"Found config file at {config}")
        break
config = yaml.safe_load(config.open())

# Setup apps
apps = {key: QuaysideApp(**val) for key, val in config.items()}

# Setup argument parser
parser = argparse.ArgumentParser("quayside")
add_verbosity_argument(parser)
subparsers = parser.add_subparsers(dest="cmd")
subparsers.required = True
for cmd, app in apps.items():
    subparser = subparsers.add_parser(cmd, add_help=False)
    app.add_arguments(subparser)
args, unknown_args = parser.parse_known_args()
configure_logger(args)

app = QuaysideApp(config[args.cmd]["container"])
app.run(*unknown_args, **vars(args))
