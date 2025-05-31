# Peyara Remote Mouse v2.0.0 - Remote Code Execution (RCE)

## Vulnerability Description
Peyara Remote Mouse v2.0.0 contains an unauthenticated remote code execution vulnerability in its WebSocket command interface (port 1313). The application fails to validate or sanitize simulated keyboard input commands received via WebSocket connections, allowing attackers to chain malicious keyboard events that execute arbitrary system commands. This vulnerability can be exploited remotely without authentication to gain full system compromise.
Remote Access Setup Procedure:

    Install Peyara Remote Mouse

        Download and install the Peyara Remote Mouse application on the Windows target system.

    Configure Netcat Listener

        Open a terminal and execute the following command to start a Netcat listener on port 4444:
        sh

    nc -nlvp 4444

Execute Exploit Script

    Run the provided script to establish a reverse shell connection. Upon successful execution, you will gain remote access to the target system"
