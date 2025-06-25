import subprocess
import argparse
import tempfile
import os

def run_handshake(host: str, port: int):
    keylog = tempfile.NamedTemporaryFile(delete=False)
    keylog_path = keylog.name
    keylog.close()

    cmd = [
        'openssl', 's_client',
        '-connect', f'{host}:{port}',
        '-tls1_3',
        '-msg',
        '-keylogfile', keylog_path
    ]
    print(f"[RUN] {' '.join(cmd)}\n")

    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Wait until TLS handshake completes (detect by handshake complete message)
    output_lines = []
    handshake_done = False
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        output_lines.append(line)
        print(f"[SERVER OUTPUT] {line.strip()}")
        # This line appears after handshake completes
        if 'SSL handshake has read' in line or 'Verify return code:' in line:
            handshake_done = True
            break

    if not handshake_done:
        print("[ERROR] TLS handshake did not complete.")
        proc.terminate()
        os.unlink(keylog_path)
        return

    # Send valid HTTP request inside TLS session
    http_request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "User-Agent: curl/7.81.0\r\n"
        "Accept: */*\r\n"
        "Accept-Encoding: gzip, deflate\r\n"
        "Accept-Language: en-US,en;q=0.9\r\n"
        "Upgrade-Insecure-Requests: 1\r\n"
        "Connection: close\r\n"
        "\r\n"
    )

    print(f"[SEND] HTTP Request:\n{http_request}")
    proc.stdin.write(http_request)
    proc.stdin.flush()

    # Read all remaining output until connection closes
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        output_lines.append(line)

    print("\n===== Annotated TLS + HTTPS Exchange =====")
    last_dir = None
    for raw in output_lines:
        line = raw.rstrip()
        if line.startswith('>>>'):
            last_dir = 'CLIENT'
            direction = 'CLIENT -> SERVER'
        elif line.startswith('<<<'):
            last_dir = 'SERVER'
            direction = 'SERVER -> CLIENT'
        else:
            if last_dir == 'CLIENT':
                direction = 'CLIENT APPLICATION DATA'
            elif last_dir == 'SERVER':
                direction = 'SERVER APPLICATION DATA'
            else:
                direction = 'APPLICATION DATA'
        print(f"[{direction:23}] {line}")

    # Print keylog contents
    print(f"\n[KEYLOG FILE] {keylog_path}")
    with open(keylog_path, 'r') as f:
        for line in f:
            print(f"[KEYLOG] {line.strip()}")

    os.unlink(keylog_path)


def main():
    parser = argparse.ArgumentParser(
        description="Capture and label TLS handshake messages with OpenSSL"
    )
    parser.add_argument("--host", required=True, help="Target hostname or IP")
    parser.add_argument("--port", type=int, default=443, help="Target port (default: 443)")
    args = parser.parse_args()
    run_handshake(args.host, args.port)


if __name__ == '__main__':
    main()
