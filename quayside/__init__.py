import docker


class QuaysideApp:
    def __init__(self, container) -> None:
        self._client = docker.from_env()
        self._container = container

    def run(self, *args, **kwargs):
        container = self._client.containers.run(self._container, *args, detach=True)
        for line in container.logs(stream=True):
            print(line.strip().decode())
