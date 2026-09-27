from __future__ import annotations

import argparse


async def _client(args: argparse.Namespace) -> None:
    import json

    from .dbus.client import Client

    async with Client() as client:
        if args.list:
            await client.list_config()
        elif args.reset_mouse:
            await client.reset_mouse()
        elif args.send is not None:
            await client.send_hotkey(args.send, args.send_delay or 0)
        elif args.new_context is not None:
            new_context_name, new_context_json = args.new_context
            await client.set_context(
                {'name': new_context_name, 'keys': json.loads(new_context_json)}, not args.disable_common
            )
        elif args.reload:
            await client.reload()
        elif args.default_context:
            await client.set_default_context()


async def _daemon(args: argparse.Namespace) -> None:
    from .daemon import Daemon

    await Daemon(permanent=args.permanent, debug=args.debug).run()


async def _run(args: argparse.Namespace) -> None:
    if (
        args.list
        or args.reset_mouse
        or args.send is not None
        or args.new_context is not None
        or args.reload
        or args.default_context
    ):
        await _client(args)
    else:
        await _daemon(args)


def main() -> None:
    parser = argparse.ArgumentParser(prog='hotkeygen')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--send')
    parser.add_argument('--send-delay', type=int)
    parser.add_argument('--default-context', action='store_true')
    parser.add_argument('--new-context', nargs=2, metavar=('new-context-name', 'new-context-json'))
    parser.add_argument('--disable-common', action='store_true')
    parser.add_argument('--reload', action='store_true')
    parser.add_argument('--permanent', action='store_true')
    parser.add_argument('--reset-mouse', action='store_true')
    args = parser.parse_args()

    import uvloop

    uvloop.run(_run(args))


if __name__ == '__main__':
    main()
