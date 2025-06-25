# ssh_handshake_parsed.py
# Captures and annotates raw SSH handshake and command execution using OpenSSH client
# Parses which debug messages are sent by CLIENT vs SERVER and labels application data
# Usage: python ssh_handshake_parsed.py --host <hostname> [--port <port>] [--user <username>] [--cmd <command>]

import subprocess
import argparse


def run_ssh(host: str, port: int, user: str, cmd_to_run: str):
    # Build ssh command with maximum verbosity
    target = f"{user}@{host}" if user else host
    cmd = [
        'ssh',
        '-vvv',               # verbose debug
        '-o', 'BatchMode=yes',
        '-o', 'StrictHostKeyChecking=no',
        '-p', str(port),
        target,
        cmd_to_run
    ]
    print(f"[RUN] {' '.join(cmd)}\n")

    # Launch ssh, capture stderr for debug, stdout for command output
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    print("\n===== Annotated SSH Handshake & Command Execution =====")
    last_dir = None
    # Read stderr for handshake debug
    for stderr_line in proc.stderr:
        line = stderr_line.strip()
        direction = 'DEBUG'
        # Identify sending vs receiving based on keywords
        if 'sending' in line or 'Sent' in line:
            direction = 'CLIENT -> SERVER'
            last_dir = 'CLIENT'
        elif 'receiving' in line or 'Received' in line or 'server version' in line:
            direction = 'SERVER -> CLIENT'
            last_dir = 'SERVER'
        # Print annotated debug
        print(f"[{direction:17}] {line}")

    # Read stdout for command output
    stdout_data = proc.stdout.read()
    if stdout_data:
        for out_line in stdout_data.splitlines():
            print(f"[SERVER APP DATA] {out_line}")

    proc.wait()


def main():
    parser = argparse.ArgumentParser(
        description="Capture and label SSH handshake messages with OpenSSH"
    )
    parser.add_argument("--host", required=True, help="Target hostname or IP")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--user", default='', help="Username for SSH login (default: current user)")
    parser.add_argument(
        "--cmd", default='echo SSH_HANDSHAKE_SUCCESS',
        help="Command to run on remote host after handshake"
    )
    args = parser.parse_args()
    run_ssh(args.host, args.port, args.user, args.cmd)


if __name__ == '__main__':
    main()