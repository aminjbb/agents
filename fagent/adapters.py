"""Real JSON-over-stdio command adapter. The host command owns tool sandboxing."""
import asyncio
import json
import sys

from .protocol import ProtocolError, require
from .registry import unique_keys


class CommandAdapter:
    def __init__(self, config):
        require(isinstance(config, dict), "Adapter config must be an object")
        command = config.get("command")
        require(isinstance(command, list) and bool(command) and
                all(isinstance(arg, str) and bool(arg) for arg in command),
                "Adapter command must be a nonempty argument array")
        timeout = config.get("timeout_seconds", 300)
        require(type(timeout) in (int, float) and 0 < timeout <= 3600, "Invalid adapter timeout")
        simulation = config.get("simulation", False)
        require(type(simulation) is bool, "simulation must be boolean")
        self.command, self.timeout, self.simulation = command, timeout, simulation

    async def invoke(self, packet):
        process = await asyncio.create_subprocess_exec(
            *self.command, cwd=packet["request"]["project_root"],
            creationflags=0x08000000 if sys.platform == "win32" else 0,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

        async def read_limited(stream):
            chunks, size = [], 0
            while chunk := await stream.read(65536):
                size += len(chunk)
                require(size <= 1048576, "Adapter output exceeds 1 MiB stream limit")
                chunks.append(chunk)
            return b"".join(chunks)

        async def exchange():
            process.stdin.write(json.dumps(packet, ensure_ascii=False).encode("utf-8"))
            await process.stdin.drain()
            process.stdin.close()
            output, _, _ = await asyncio.gather(
                read_limited(process.stdout), read_limited(process.stderr), process.wait())
            require(process.returncode == 0, f"Adapter exited with code {process.returncode}")
            result = json.loads(output.decode("utf-8-sig"), object_pairs_hook=unique_keys)
            require(isinstance(result, dict), "Adapter must return one JSON object")
            return result

        operation = asyncio.create_task(exchange())
        try:
            return await asyncio.wait_for(operation, self.timeout)
        except asyncio.TimeoutError as error:
            raise ProtocolError("Adapter timed out; inspect side effects before retry") from error
        finally:
            if process.returncode is None:
                process.kill()
            await process.wait()
            if not operation.done():
                operation.cancel()
            await asyncio.gather(operation, return_exceptions=True)
