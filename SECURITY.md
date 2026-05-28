# Security policy

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Instead, use one of the private channels below:

- **GitHub private vulnerability reporting** (preferred): open a report at <https://github.com/Alpaq92/FlagHub/security/advisories/new>.
- **Email**: `noreply@github.com` (placeholder — replace with a monitored address before relying on this).

Please include:

- A clear description of the vulnerability and its impact
- Steps to reproduce (or a proof-of-concept)
- Affected version(s) — commit SHA, release tag, or branch
- Your contact info if you'd like credit in the advisory

## What to expect

| Stage | Target |
|---|---|
| Acknowledgement | within **3 business days** of report |
| Triage / initial assessment | within **7 business days** |
| Fix and coordinated disclosure | depends on severity; high/critical issues are prioritised |

We follow [coordinated disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure) — please give us reasonable time to ship a fix before publishing details.

## Supported versions

FlagHub is a fork of [`madebybowtie/FlagKit`](https://github.com/madebybowtie/FlagKit). Only the **latest `main`** of this fork is actively patched. Upstream-only issues should be reported to upstream.

| Version | Patched |
|---|---|
| `main` (latest) | ✅ |
| Tagged releases | latest tag only |
| Anything in upstream FlagKit | report upstream |

## Out of scope

- Vulnerabilities in third-party dependencies — please report directly to that project (or to GitHub via Dependabot).
- Issues that require a malicious local environment / compromised build server.
- Theoretical issues without a reproducible exploit path.

## Hall of fame

Researchers credited in published advisories will be listed here.
