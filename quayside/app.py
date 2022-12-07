import docker
from pathlib import Path


class QuaysideApp:
    def __init__(self, /, container, cwd=None) -> None:
        self._client = docker.from_env()
        self._container = container
        self._cwd = cwd

    def run(self, *args, **kwargs):
        mounts = []
        if self._cwd:
            logger.debug(f'Mount {Path(".")} at {self._cwd}')
            mounts.append(docker.types.Mount(self._cwd, str(Path("."))))
        container = self._client.containers.run(
            self._container, args, mounts=mounts, detach=True
        )
        for line in container.logs(stream=True):
            print(line.strip().decode())

    def add_arguments(self, parser):
        pass
