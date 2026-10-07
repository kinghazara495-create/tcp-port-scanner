# TCP Port Scanner

A 14-line TCP port scanner written with the Python standard library, as a
learning exercise in how the TCP three-way handshake behaves when you use raw
sockets instead of a library.

```bash
python port_scanner.py
```

```
ENTER YOUR IP: 127.0.0.1
22 PORT IS OPEN
80 PORT IS CLOSE
...
```

Scans ports `21, 22, 23, 25, 53, 80, 110, 443, 3306, 8080` and prints which are
open. No dependencies.

---

## Authorised use only

**Scan only hosts you own or have explicit written permission to test.**

Port scanning is lawful reconnaissance on your own systems and on systems where
you hold authorisation. Running it against someone else's infrastructure without
permission is a computer crime in most jurisdictions, including under Pakistan's
PECA and the IT Act, the UK Computer Misuse Act, and equivalents elsewhere.
"Good intentions" and "I was only looking" have never been a successful defence.

This repository ships the code **as written**, with no built-in restriction on
target. That is a deliberate choice to publish the learning artefact unmodified,
and it is also a real weakness: the script will point at any host you type. Do
not use it on a network that is not yours.

---

## Known limitations

These are real and worth understanding rather than fixing quietly. A scanner that
reports its own gaps is more useful than one that hides them.

### 1. It cannot tell "closed" from "filtered"

This is the important one. `socket.connect_ex()` returns an **errno**, not a
boolean. Only `0` means the port is open. Every other value is a different
condition, and this script collapses all of them into one message:

| errno | Name | Actual meaning |
|---|---|---|
| `0` | — | **port is open** |
| `111` | `ECONNREFUSED` | closed; host answered, nothing listening |
| `110` | `ETIMEDOUT` | **filtered**; packets dropped, usually by a firewall |
| `113` | `EHOSTUNREACH` | host unreachable |
| `101` | `ENETUNREACH` | network unreachable |
| `100` | `ETIMEDOUT` (non-blocking) | connection in progress |

So `PORT IS CLOSE` actually means "not open", which includes *filtered* and
*unreachable*. A host with a strict firewall and a closed host both print
identically. **A port scanner that cannot distinguish refused from filtered is
not telling you what is there**, only what is not answering.

### 2. Typo in the output

`PORT IS CLOSE` should read `CLOSED`. It is printed output, so it is visible to
everyone who runs it.

### 3. Sequential, single-threaded

Ten ports at a one-second timeout each means up to ten seconds of waiting when
everything is filtered. Real scanners use a thread pool; DNS lookups and connects
are IO-bound, which is exactly the workload threads are good at.

### 4. The socket can leak

`socket.close()` is called at the end of each iteration, but if
`connect_ex()` raises, `close()` is never reached. A `with socket.socket(...) as
sock:` block makes cleanup automatic.

### 5. No service identification

An open port is labelled with its number only. Mapping `5432` to "PostgreSQL"
is the next step.

### 6. Naming

The socket object is called `port` while the port number is `i`, which reads
backwards. Renaming to `sock` and `port` respectively would be clearer.

### 7. No reverse DNS or banner grab

Nothing here resolves the PTR record or reads what service says on connect.

---

## What it does correctly

Worth saying, because a short script can still get the fundamentals right:

- **A fresh socket per attempt.** Created inside the loop, so no state leaks
  between ports. This is the bug most beginner scanners have: reusing one socket
  works until it silently returns a stale result for every port after the first,
  which looks exactly like "the whole network is down."
- **A timeout is set.** Without `settimeout(1)` a single filtered host hangs the
  entire scan indefinitely.
- **`connect_ex()` instead of `connect()`.** Returns a code instead of raising,
  so a closed port does not need a `try`/`except` on every iteration. On a scan
  that is ten exception paths avoided.
- **No dependencies.** `socket` is in the standard library.

---

## Licence

MIT. See `LICENSE`.