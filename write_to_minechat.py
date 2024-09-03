import asyncio
from asyncio.streams import StreamWriter
import json
import logging
from pathlib import Path

import aiofiles
from configargparse import ArgParser, Namespace

from socket_utils import connect_to_chat

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
    parser.add('--user_hash',
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


def process_server_response(raw_response: bytes) -> tuple[str]:
    text_response = raw_response.decode().strip()

    try:
        json_response = json.loads(text_response)
    except json.JSONDecodeError:
        json_response = None

    logger.debug(text_response)

    return text_response, json_response


async def register(host: str, port: int, user_name: str) -> str:
    async with connect_to_chat(host, port) as (reader, writer):
        while True:
            text_response, json_response = process_server_response(
                await reader.readline()
            )

            if text_response == AUTH_REQUIRED:
                writer.write('\n'.encode())
                await writer.drain()
            elif text_response == ENTER_NICKNAME:
                writer.write(f'{user_name}\n'.encode())
                await writer.drain()
                logger.debug(user_name)
            elif json_response is not None:
                async with aiofiles.open('credentials.json', 'w') as stream:
                    await stream.write(json.dumps(json_response,
                                                  ensure_ascii=True,
                                                  indent=2))
                return json_response['account_hash']


async def authorize(writer: StreamWriter, user_hash: str) -> None:
    writer.write(f'{user_hash}\n'.encode())
    await writer.drain()
    logger.debug(user_hash)


async def submit_message(host: str,
                         port: int,
                         user_hash: str,
                         message: str) -> None:
    async with connect_to_chat(host, port) as (reader, writer):
        while True:
            text_response, json_response = process_server_response(
                await reader.readline()
            )

            if text_response == AUTH_REQUIRED:
                await authorize(writer, user_hash)
            elif text_response == CHAT_GREETING:
                writer.write(f'{message}\n\n'.encode())
                await writer.drain()
                logger.debug(message)
                return
            elif json_response is None:
                logger.error('Invalid token. Check credentials '
                             'or leave it empty to register new user.')
                return


async def get_user_credentials() -> str | None:
    user_hash = None
    try:
        with open('credentials.json', 'r') as stream:
            credentials = json.loads(stream.read())
        user_hash = credentials.get('account_hash', '')
    except FileNotFoundError:
        logger.info('User credentials not found.')
    except json.JSONDecodeError:
        logger.warning('Can\'t parse user credentials.')

    if user_hash:
        return user_hash


async def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG
    )

    args = parse_arguments()
    user_name = args.user_name.replace(r'\n', '')
    user_message = args.message.replace(r'\n', ' ')
    user_hash: str = args.user_hash

    if not user_hash:
        user_hash = await get_user_credentials()

    if not user_hash:
        user_hash = await register(args.host, args.port, user_name)

    await submit_message(args.host, args.port, user_hash, user_message)


if __name__ == '__main__':
    asyncio.run(main())
