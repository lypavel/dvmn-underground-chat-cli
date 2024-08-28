import asyncio
import sys
from socket import gaierror

from configargparse import ArgParser, Namespace

AUTH_REQUIRED = (
    'Hello %username%! Enter your personal hash '
    'or leave it empty to create new account.'
)

CHAT_GREETING = (
    'Welcome to chat! Post your message below. End it with an empty line.'
)


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
    parser.add('--message', type=str, required=True, help='Message to send')

    args, _ = parser.parse_known_args()

    return args


async def send_message(host: str,
                       port: int,
                       user_hash: str,
                       message: str) -> None:
    try:
        reader, writer = await asyncio.open_connection(
            host, port
        )
        while True:
            raw_response = await reader.readline()
            text_response = raw_response.decode().strip()
            print(text_response)

            if text_response == AUTH_REQUIRED:
                writer.write(f'{user_hash}\n'.encode())
                await writer.drain()
            elif text_response == CHAT_GREETING:
                writer.write(f'{message}\n\n'.encode())
                await writer.drain()
                break
    except gaierror:
        print('Connection error: check your internet connection.',
              file=sys.stderr)


def main() -> None:
    args = parse_arguments()

    print(args)

    asyncio.run(send_message(args.host,
                             args.port,
                             args.hash,
                             args.message))


if __name__ == '__main__':
    main()
