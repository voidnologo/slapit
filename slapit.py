#!/usr/bin/env python3

import argparse
import configparser
from pathlib import Path
import textwrap

from colorama import init, Fore, Style
from twitter import OAuth, Twitter


def get_client():
    CREDS_PATH = Path.home().joinpath('.twitter_api')
    CREDS_FILE = CREDS_PATH.joinpath('twitter_creds.ini')

    config_file = configparser.ConfigParser()
    config_file.read(CREDS_FILE)
    return Twitter(
        auth=OAuth(
            config_file['TWITTER_CREDS']['token'],
            config_file['TWITTER_CREDS']['token_secret'],
            config_file['TWITTER_CREDS']['consumer_key'],
            config_file['TWITTER_CREDS']['consumer_secret']
        )
    )


def format_message(message):
    return ' '.join(message)


def say(args):
    client = get_client()
    client.statuses.update(status=format_message(args.message))


def get(args):
    client = get_client()
    if args.user:
        messages = client.statuses.user_timeline(
            screen_name=args.user, count=args.count, tweet_mode='extended'
        )
    else:
        messages = client.statuses.home_timeline(count=args.count, tweet_mode='extended')
    indent = ' ' * 4
    for message in messages:
        print(f'{Fore.GREEN + message["user"]["name"]}    {message["created_at"]}')
        print(
            '\n'.join(
                textwrap.wrap(
                    f'{message["full_text"]}',
                    width=54,
                    initial_indent=indent,
                    subsequent_indent=indent
                )
            )
        )
        url = f'https://twitter.com/i/web/status/{message["id"]}'
        print(f'{indent}{Fore.CYAN + url}')
        print('\n')


def tell(args):
    client = get_client()
    client.direct_messages.events.new(
        _json={
            "event": {
                "type": "message_create",
                "message_create": {
                    "target": {
                        "recipient_id": client.users.show(screen_name=args.recipient)["id"]},
                    "message_data": {
                        "text": format_message(args.message)}
                }
            }
        }
    )


parser = argparse.ArgumentParser(prog='SlapIt', formatter_class=argparse.RawDescriptionHelpFormatter)
subparsers = parser.add_subparsers()

parser_s = subparsers.add_parser('say', aliases=['s'])
parser_s.add_argument('message', nargs='+')
parser_s.set_defaults(func=say)

parser_g = subparsers.add_parser('get', aliases=['g'])
parser_g.add_argument('count', type=int, default=5, nargs='?')
parser_g.add_argument('-u', '--user', dest='user')
parser_g.set_defaults(func=get)

parser_t = subparsers.add_parser('tell', aliases=['t'])
parser_t.add_argument('recipient')
parser_t.add_argument('message', nargs='+')
parser_t.set_defaults(func=tell)


if __name__ == '__main__':
    init(autoreset=True)
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        print(f'An error occured.  {type(e).__name__}::{str(e)}')
