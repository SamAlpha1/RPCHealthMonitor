#!/usr/bin/env python3
"""Read-only health checks for EVM-compatible JSON-RPC endpoints."""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from typing import Any
from urllib import request


def rpc_call(url: str, method: str, params: list[Any], timeout: float) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "RPCHealthMonitor/1.0"})
    with request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode())
    if "error" in body:
        raise RuntimeError(body["error"])
    return body.get("result")


def check_endpoint(url: str, stale_seconds: int, timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        chain_id = int(rpc_call(url, "eth_chainId", [], timeout), 16)
        block_hex = rpc_call(url, "eth_blockNumber", [], timeout)
        block_number = int(block_hex, 16)
        block = rpc_call(url, "eth_getBlockByNumber", [block_hex, False], timeout)
        block_ts = int(block["timestamp"], 16)
        age = max(0, int(time.time() - block_ts))
        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        healthy = age <= stale_seconds
        return {
            "url": url,
            "healthy": healthy,
            "chain_id": chain_id,
            "block_number": block_number,
            "block_time_utc": datetime.fromtimestamp(block_ts, tz=timezone.utc).isoformat(),
            "block_age_seconds": age,
            "latency_ms": latency_ms,
            "error": None,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "url": url,
            "healthy": False,
            "chain_id": None,
            "block_number": None,
            "block_time_utc": None,
            "block_age_seconds": None,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": str(exc),
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check EVM JSON-RPC endpoint health.")
    parser.add_argument("urls", nargs="*", help="RPC URLs. If omitted, RPC_URLS is used.")
    parser.add_argument("--stale-seconds", type=int, default=180, help="Maximum acceptable latest-block age.")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout per RPC call in seconds.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a table.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    urls = list(args.urls)
    if not urls:
        urls = [item.strip() for item in os.getenv("RPC_URLS", "").split(",") if item.strip()]
    if not urls:
        raise SystemExit("Provide at least one RPC URL or set RPC_URLS.")

    results = [check_endpoint(url, args.stale_seconds, args.timeout) for url in urls]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for item in results:
            state = "OK" if item["healthy"] else "FAIL"
            if item["error"]:
                print(f"[{state}] {item['url']}  latency={item['latency_ms']}ms  error={item['error']}")
            else:
                print(
                    f"[{state}] {item['url']}  chain={item['chain_id']}  block={item['block_number']}  "
                    f"age={item['block_age_seconds']}s  latency={item['latency_ms']}ms"
                )
    return 0 if all(item["healthy"] for item in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
