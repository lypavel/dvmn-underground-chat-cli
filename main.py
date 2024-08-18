import asyncio
from environs import Env


async def read_messages(host: str, port: int) -> None:
    while True:
        reader, _ = await asyncio.open_connection(
            host, port
        )

        data = await reader.readline()
        print(data.decode().strip())


def main() -> None:
    env = Env()
    env.read_env()

    host = env.str('HOST')
    port = env.int('PORT')

    asyncio.run(read_messages(host, port))


if __name__ == '__main__':
    main()
