import asyncio
import json
import logging
from pathlib import Path
from socket import gaierror
import sys

import aiofiles
from configargparse import ArgParser, Namespace

AUTH_REQUIRED = (
    'Hello %username%! Enter your personal hash '
    'or leave it empty to create new account.'
)

CHAT_GREETING = (
    'Welcome to chat! Post your message below. End it with an empty line.'
)

ENTER_NICKNAME = 'Enter preferred nickname below:'

logger = logging.getLogger(Path(__file__).name)


def parse_arguments() -> Namespace:
    parser = ArgParser(default_config_files=('.env', ))
    parser.add('--host',
               '--HOST',
               type=str,
               default='minechat.dvmn.org',
               help='Host name')
    parser.add('--port', '--WRITE_PORT', type=int, default=5050, help='Port')
    parser.add('--hash',
               '--USER_HASH',
               type=str,
               default='',
               help='Chat user hash')
    parser.add('--user_name',
               '--USER_NAME',
               type=str,
               default='anonymous',
               help='User name')
    parser.add('--message', type=str, required=True, help='Message to send')

    args, _ = parser.parse_known_args()

    return args


async def send_message(host: str,
                       port: int,
                       user_hash: str,
                       user_name: str,
                       message: str) -> None:
    try:
        reader, writer = await asyncio.open_connection(
            host, port
        )
        while True:
            raw_response = await reader.readline()
            text_response = raw_response.decode().strip()
            logger.debug(text_response)

            if text_response == AUTH_REQUIRED:
                if not user_hash:
                    writer.write('\n'.encode())
                    await writer.drain()
                    continue

                writer.write(f'{user_hash}\n'.encode())
                await writer.drain()
                logger.debug(user_hash)
            elif text_response == ENTER_NICKNAME:
                writer.write(f'{user_name}\n'.encode())
                await writer.drain()
                logger.debug(user_name)

            elif text_response == CHAT_GREETING:
                writer.write(f'{message}\n'.encode())
                await writer.drain()
                logger.debug(message)
                break
            elif json.loads(text_response) is None:
                logger.error('Invalid token. Check credentials or leave it empty to register new user.')
                break
            elif json.loads(text_response):
                async with aiofiles.open('credentials.json', 'w') as stream:
                    await stream.write(json.dumps(json.loads(text_response), ensure_ascii=True, indent=2))

    except gaierror:
        print('Connection error: check your internet connection.',
              file=sys.stderr)


def main() -> None:
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG
    )

    args = parse_arguments()
    user_hash = args.hash

    if not args.hash:
        try:
            with open('credentials.json', 'r') as stream:
                credentials = json.loads(stream.read())
            user_hash = credentials.get('account_hash', '')
        except FileNotFoundError:
            logger.info('User credentials not found.')
        except json.JSONDecodeError:
            logger.warning('Can\'t parse user credentials.')

    asyncio.run(send_message(args.host,
                             args.port,
                             user_hash,
                             args.user_name,
                             args.message))


if __name__ == '__main__':
    main()
