import logging
from pathlib import Path

import docker

logger = logging.getLogger(__name__)


class QuaysideApp:
    def __init__(self, /, container, cwd=None) -> None:
        self._client = docker.from_env()
        self._container = container
        self._cwd = cwd

    def run(self, *args, **kwargs):
        mounts = []
        if self._cwd:
            logger.debug(f'Mount {Path(".").absolute()} at {self._cwd}')
            mounts.append(docker.types.Mount(self._cwd, str(Path(".").absolute()), type="bind"))
        else:
            logger.debug(f"Do not mount CWD.")
        container = self._client.containers.run(self._container, args, mounts=mounts, detach=True)
        for line in container.logs(stream=True):
            print(line.strip().decode())

    def add_arguments(self, parser):
        pass
