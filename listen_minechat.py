import asyncio
from datetime import datetime
from pathlib import Path
import sys
from socket import gaierror

import aiofiles
from configargparse import ArgParser, Namespace


def parse_arguments() -> Namespace:
    parser = ArgParser(default_config_files=('.env', ))
    parser.add('--host',
               '--HOST',
               type=str,
               default='minechat.dvmn.org',
               help='Host name')
    parser.add('--port',
               '--LISTEN_PORT',
               type=int,
               default=5000,
               help='Port')
    parser.add('--chat_history_file',
               '--CHAT_HISTORY_FILE',
               type=Path,
               default='./chat_history.txt',
               help='Path to file where to save chat history')

    args, _ = parser.parse_known_args()
    return args


async def read_messages(host: str,
                        port: int,
                        chat_history_file: Path) -> None:
    while True:
        try:
            reader, _ = await asyncio.open_connection(
                host, port
            )

            raw_message = await reader.readline()
            formatted_message = (
                f'[{datetime.now().strftime("%d.%m.%y %H:%M")}] '
                f'{raw_message.decode().strip()}'
            )

            async with aiofiles.open(chat_history_file, 'a') as stream:
                await stream.write(f'{formatted_message}\n')

            print(formatted_message, file=sys.stdout)
        except gaierror:
            print('Connection error: check your internet connection.',
                  file=sys.stderr)
            asyncio.sleep(10)


def main() -> None:
    args = parse_arguments()
    asyncio.run(read_messages(args.host, args.port, args.chat_history_file))


if __name__ == '__main__':
    main()
