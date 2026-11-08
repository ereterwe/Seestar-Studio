# ZWO interoperability review — 8 November 2026

Status: **OPEN — no legal clearance**. This review describes the locally audited
2.3.0b2 implementation with SeestarPy 0.8.0. B3 is built locally from this baseline after clarification by the owner.

## Technical facts

Seestar Studio is an independently developed Windows client. Protocol knowledge
comes from [SeestarPy](https://github.com/astronomyk/seestarpy), its installed
source and documentation, and the previously documented S50/S50 Pro tests.
No proprietary ZWO application code is incorporated into Seestar Studio.

The user supplies an existing local PEM, or selects an APK/XAPK obtained by the
user. `setup_service.py` calls SeestarPy's `extract_pem_from_apk`, rather than its
command-line entry point. The library scans printable ASCII strings in exactly
`lib/arm64-v8a/libopenssllib.so` and `lib/armeabi-v7a/libopenssllib.so` for PEM
private-key blocks. This implementation does not decrypt or execute those
libraries. XAPK-contained APKs are temporarily staged locally with size/count
limits; temporary files are removed. No APK download is part of setup.

Import validates an unencrypted RSA private key and identifies duplicates by a
hash of the public key. Imported keys use randomly named PEM files in the private
user profile. The Windows directory/file DACL grants the current user and SYSTEM
access; reparse paths are rejected. Files are exclusively created before writing.
Configuration stores a relative key filename, not the key value. Activating a
replacement for a working configuration requires confirmation. Cancellation and
failed imports discard newly created inactive keys. Existing SeestarPy key lookup
and environment configuration retain precedence.

SeestarPy `auth.py` requests a challenge, signs it using RSA PKCS#1 v1.5/SHA-1,
and sends a base64 signature in `verify_client`. The private key itself is not
sent by this code. The inspected implementation does not derive the signing key
from an account or device serial number; its comments describe a common key.
This is evidence about this implementation, not a guarantee for future firmware.
LAN RPC is not represented as an encrypted transport. The connection check is
an explicitly initiated, bounded authentication/status exchange, not a movement
or capture command.

The application does not invoke SeestarPy's `--stdout` extraction option.
Import errors are sanitized; keys and APKs are excluded from Git and explicit
packaging inputs. Source and packaged-code scans found no real key material in
the audited b2 scope. This does not justify logging protocol secrets or sharing
private profile directories. No real PEM/APK was opened or extracted for this
audit; setup tests generate disposable synthetic keys.

## Questions requiring legal review

The purpose is interoperability, but that purpose alone does not establish an
exception. Review the actual acquisition/use rights for the APK, whether required
information is otherwise readily available, whether processing is necessary and
limited, and how the extracted key may be used. Establish whether the operation
falls within observation/testing, reproduction, translation or another category.
[§ 69d UrhG](https://www.gesetze-im-internet.de/urhg/__69d.html) and
[§ 69e UrhG](https://www.gesetze-im-internet.de/urhg/__69e.html) require a
fact-specific assessment. Section 69e imposes conditions on obtaining
interoperability information and limits its subsequent use/disclosure.

Authentication is a technical access mechanism even if the inspected strings
are unencrypted. Review possible protection-measure provisions and their exact
relationship to computer-program rules; do not assume either that every access
check is protected or that interoperability automatically permits bypassing it.
Review relevant ZWO application/device terms, entitlement to use the supplied
key, trade-secret questions and the legal position of users in their jurisdiction.
[§ 69g UrhG](https://www.gesetze-im-internet.de/urhg/__69g.html) addresses other
applicable law and certain conflicting contractual terms. No applicable ZWO
contract or written permission has been established by this audit.

Before treating the import workflow as legally cleared, obtain a documented
assessment of these facts, including whether ZWO offers a supported interface or
permission. Do not publish an APK, extracted private key, or instructions that
imply unrestricted entitlement to third-party secrets. GPL licensing of the
client or SeestarPy does not license proprietary ZWO material.

## Brands and independence

The About dialog contains an explicit German/English independence notice: the
project is neither developed nor officially supported by ZWO. Product names
identify compatible hardware; they are not a claim of sponsorship. The app's own
SVG/PNG/ICO has documented project authorship (`assets/ICON-LICENSE.txt`). No ZWO
logo or product photograph is a release input. Trademark/name clearance for
“Seestar Studio” remains OPEN; the presence of a disclaimer is not a legal ruling.

References checked against official legal/primary sources on 8 November 2026.
This document contains no private key value and makes no binding legal conclusion.
