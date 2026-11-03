# DATUM Gateway for Home Assistant

Read one [DATUM Gateway](https://github.com/OCEAN-xyz/datum_gateway) from Home Assistant. One config entry is one gateway. A host that runs mainnet, testnet, signet and regtest side by side is four entries.

This is a custom component. It is not in Home Assistant core and not in the default HACS catalog.

## What it reads

Every 30 seconds, without a password:

| Endpoint | Used for |
|----------|----------|
| `GET /v1/decentralized_client_stats` | ready state, pool host, share counters, uptime |
| `GET /v1/stratum_server_info` | estimated hashrate (TH/s), connections, subscriptions, Stratum threads |
| `GET /v1/current_stratum_job` | block height, reward, template size. A JSON `error` (no job yet) leaves those sensors empty |
| `GET /v1/thread_stats` | number of Stratum threads |

`/v1/coinbaser` is not called. That payload is a list of payout addresses, and those addresses do not belong in Home Assistant state.

`/v1/configuration` is not called, neither `GET` nor `POST`. A `POST` can change the payout address and restart the gateway, and a successful response echoes `rpcpassword` if one was sent. There is no separate restart endpoint. Control of the gateway stays on the gateway.

The client list (`/v1/stratum_client_list`) needs HTTP Digest and is not polled. Connection count comes from the public Stratum info instead. Worker usernames are often wallet strings; they are not copied into entity state.

## Requirements

- Home Assistant 2024.11 or newer (`ConfigEntry.runtime_data`)
- A gateway built with the JSON API (`api.json_api: true`, listen port usually `7152`)
- The URL must be reachable from the Home Assistant host, not from the browser you use to add the integration

The example config listens on a specific address. `http://127.0.0.1:7152` fails when the process is bound only to a LAN address. Use the address from `api.listen_addr`.

Keep the API on a trusted network. The public stats endpoints have no authentication.

## Install

HACS: Custom repositories, category Integration, `https://github.com/vincenzopalazzo/ha-datum-gateway`.

By hand:

```bash
mkdir -p /path/to/config/custom_components
cp -R custom_components/datum_gateway /path/to/config/custom_components/datum_gateway
```

Restart Home Assistant. **Settings → Devices & services → Add integration → DATUM Gateway**.

| Field | Value |
|-------|--------|
| API URL | Base URL only. `http://127.0.0.1:7152` if the API listens on loopback, otherwise the listen address |
| Name | Optional device name, for example `mainnet` |

The same URL cannot be added twice.

## Entities

Ready is on for `Ready` and for `Non-Pooled Mode and Ready`. It is off for `Not Ready`, `Waiting…` and `Block template error`.

Estimated hashrate is the gateway's own figure in TH/s. A miner at a few hundred GH/s reads as a small fraction of 1 TH/s; the sensor keeps six decimal places. A sample older than 180 seconds is excluded by the gateway and shows as 0, which is not the same as "the API failed".

Share counters reset when the gateway process restarts. They count pool responses, not local Stratum acceptance.

## Development

```bash
python3 tests/test_parser.py
python3 -m py_compile custom_components/datum_gateway/*.py
```

The parser has no Home Assistant dependency. The component itself is not executed by that test.
