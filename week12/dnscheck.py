# dns_dot_query_parsed.py
# Demonstrates DNS over TLS (DoT) handshake and DNS query/response parsing
# Logs handshake details, raw DNS wire data, and parsed response
# Usage: pip install dnspython; python dns_dot_query_parsed.py --host <hostname> [--port <port>] --name <domain>

import socket
import ssl
import argparse
import dns.message


def main():
    parser = argparse.ArgumentParser(description="Perform DNS over TLS query with detailed logging.")
    parser.add_argument("--host", required=True, help="DoT server hostname or IP")
    parser.add_argument("--port", type=int, default=853, help="DoT port (default: 853)")
    parser.add_argument("--name", required=True, help="Domain name to query")
    args = parser.parse_args()
    host, port, qname = args.host, args.port, args.name

    # 1. Create SSL context for TLS1.2
    context = ssl.create_default_context()
    context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3
    try:
        context.minimum_version = ssl.TLSVersion.TLSv1_2
    except AttributeError:
        pass  # older Python
    context.keylog_filename = 'dns_tls_keylog.txt'
    print(f"[STEP 1] SSL context: TLS1.2 enforced, keylog at {context.keylog_filename}")

    # 2. Connect and handshake
    with socket.create_connection((host, port)) as sock:
        with context.wrap_socket(sock, server_hostname=host) as ssock:
            print(f"[STEP 2] Handshake complete: Protocol={ssock.version()}, Cipher={ssock.cipher()[0]}")

            # 3. Build DNS query and show wire format
            query = dns.message.make_query(qname, dns.rdatatype.A)
            wire = query.to_wire()
            length = len(wire).to_bytes(2, 'big')
            print(f"[STEP 3] Sending DNS query for {qname} (length={len(wire)}):")
            print(wire.hex())

            # 4. Send query
            ssock.sendall(length + wire)

            # 5. Receive raw response
            resp_data = ssock.recv(4096)
            print(f"[STEP 4] Raw response (hex): length_prefix={resp_data[:2].hex()}, payload={resp_data[2:].hex()}")

            # 6. Parse DNS response
            resp = dns.message.from_wire(resp_data[2:])
            print(f"[STEP 5] Parsed DNS response:")
            for answer in resp.answer:
                print(f"  {answer.name} {answer.rdtype} -> {answer.items}")

    print("[STEP 6] Connection closed.")

if __name__ == '__main__':
    main()