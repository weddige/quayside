import argparse
import logging
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Dict, List, Optional, Tuple

import docker  # type: ignore

logger = logging.getLogger(__name__)


class MappedArgument:
    def __init__(self, argument: str, value: Optional[str] = None, func: Callable[[str], str] = lambda a: a) -> None:
        self._argument = argument
        self._value = value
        self._func = func

    def __call__(self, value: str) -> "MappedArgument":
        return MappedArgument(self._argument, value, self._func)

    def map(self) -> Tuple[str, str]:
        if not self._value:
            raise RuntimeError("Value of MappedArgument is not initialized!")
        return (self._argument, self._func(self._value))


class QuaysideApp:
    def __init__(
        self,
        /,
        container: str,
        mounts: List[Dict[str, str]] = [],
        mapped_arguments: Dict[str, List[str]] = {},
        cwd: Optional[str] = None,
        cli: Optional[str] = None,
        environment: Dict[str, str] = {},
    ) -> None:
        self._client = docker.from_env()
        self._container = container
        self._mounts = mounts
        self._cwd = cwd
        self._arguments = mapped_arguments
        self._cli = cli
        self._environment = environment

    def run(self, *args: str, **kwargs: Any) -> None:
        mounts = []
        if self._cwd:
            source = str(Path(".").absolute())
            logger.debug(f"Mount {source} at {self._cwd}")
            mounts.append(docker.types.Mount(self._cwd, source, type="bind"))
        for mount in self._mounts:
            source = str(Path(mount["source"]).absolute())
            target = mount["target"]
            logger.debug(f"Mount {source} at {target}")
            mounts.append(docker.types.Mount(target, source, type="bind"))
        command: Optional[List[str]] = list(args)
        assert isinstance(command, list)
        for arg in kwargs.get("mapped_args", []) or []:
            command.extend(arg.map())
        environment = self._environment.copy()
        if self._cli:
            # Pass CLI args via environment variable
            environment[self._cli] = " ".join(command)
            # Do not pass CLI args as command
            command = None
        container = self._client.containers.run(
            self._container, command or None, environment=environment, mounts=mounts, detach=True, auto_remove=True
        )
        for line in container.logs(stream=True):
            print(line.strip().decode())

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        if arguments := self._arguments.get("cwd", []):
            if not self._cwd:
                raise RuntimeError("Mapped arguments are only possible if cwd is defined!")
            cwd = self._cwd
            for argument in arguments:
                parser.add_argument(
                    argument,
                    type=MappedArgument(argument, func=lambda path: str(PurePosixPath(cwd, path))),
                    dest="mapped_args",
                    action="append",
                )
