# Minechat messages reader and sender

Simple CLI scripts for online monitoring and saving history and sending messages to Minechat.

## Installation

1. Install [Python 3.10.12](https://www.python.org/downloads/release/python-31012/) and activate [virtual environment](https://docs.python.org/3/library/venv.html) if you need one.
2. Install dependencies with `pip`
    ```shell
    pip install -r requirements.txt
    ```
## Arguments and environment variables

You can pass parameters either via arguments in CLI or via environment variables (`.env` file at project root).

### **listen_minechat.py**

|Argument|Environment variable|Default value|Description|
|--------|--------------------|-------------|-----------|
|`--host`|`HOST`|`minechat.dvmn.org`|Chat host.|
|`--port`|`LISTEN_PORT`|`5000`|Chat port for monitoring messages.|
|`--chat_history_file`|`CHAT_HISTORY_FILE`|`./chat_history.txt`|Where to save chat history.|

### **write_to_minechat.py**

|Argument|Environment variable|Default value|Description|
|--------|--------------------|-------------|-----------|
|`--host`|`HOST`|`minechat.dvmn.org`|Chat host.|
|`--port`|`WRITE_PORT`|`5050`|Chat port for sending messages.|
|`--user_hash`|`USER_HASH`|`''`|User hash (token).|
|`--user_name`|`USER_NAME`|`anonymous`|User name.|
|`--message`|`MESSAGE`|-|Message to send. **Required.**|

### User credentials load priority

1. Environment variables
2. Command line arguments
3. `credentials.json` (created at project root after first registration)

## Usage

### Monitoring messages

```shell
python3 listen_minechat.py [-h] [--host HOST] [--port PORT] [--chat_history_file CHAT_HISTORY_FILE]
```

All message history will be saved to `CHAT_HISTORY_FILE`.

### Sending messages

```shell
python3 write_to_minechat.py [-h] [--host HOST] [--port PORT] [--user_hash USER_HASH] [--user_name USER_NAME] --message MESSAGE
```

***
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).