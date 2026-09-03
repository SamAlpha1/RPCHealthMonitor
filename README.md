# RPC Health Monitor

A lightweight command-line health checker for EVM-compatible JSON-RPC endpoints.

It measures RPC latency, chain ID, latest block height, and latest-block age so operators can quickly spot slow, stale, or unavailable endpoints.

## Features

- Checks one or many EVM JSON-RPC URLs
- Measures request latency
- Reads `eth_chainId` and `eth_blockNumber`
- Checks latest block timestamp and reports block age
- Fails with a non-zero exit code when an endpoint is unavailable or stale
- Human-readable and JSON output
- Standard-library only: no third-party Python packages

## Requirements

- Python 3.10+

## Quick start

```bash
git clone https://github.com/SamAlpha1/RPCHealthMonitor.git
cd RPCHealthMonitor
python rpc_health.py https://ethereum-rpc.publicnode.com
```

Check several endpoints:

```bash
python rpc_health.py \
  https://ethereum-rpc.publicnode.com \
  https://eth.llamarpc.com
```

Use environment configuration:

```bash
cp .env.example .env
export RPC_URLS="https://ethereum-rpc.publicnode.com,https://eth.llamarpc.com"
python rpc_health.py
```

JSON output:

```bash
python rpc_health.py https://ethereum-rpc.publicnode.com --json
```

Change the stale-block threshold:

```bash
python rpc_health.py https://ethereum-rpc.publicnode.com --stale-seconds 300
```

## Exit codes

- `0`: every endpoint passed
- `2`: at least one endpoint failed or returned a stale latest block

## Notes

This utility only performs read-only JSON-RPC calls. It never needs a wallet, seed phrase, or private key.

---

## More from SamAlpha1

Before running unfamiliar GitHub or Web3 code, scan the account and its public repositories with **[GitHub Trust Auditor](https://samalpha1.github.io/GitHubTrustAuditor/)**.

Maintained by **[SamAlpha1](https://github.com/SamAlpha1)** · Follow **[@samalpha_ on X](https://x.com/samalpha_)**
