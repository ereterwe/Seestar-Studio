# Microsoft runtime review — 8 November 2026

## Answer for this project

Microsoft redistribution terms are relevant because b3 actually ships MSVC DLLs.
There is **no established requirement to buy a Professional/Enterprise licence**
for this public GPL project. Visual Studio Community 2026 is installed locally;
its published licence provides individual-development and OSI-open-source routes.
Project suitability for that route is documented; the presence of an installation
alone is not proof of any person's compliance with their agreement.

Source: [Community 2026 terms](https://visualstudio.microsoft.com/license-terms/vs2026-ga-community/).
The official document was downloaded and hashed for the review, without accessing
accounts, activation tokens or personal licence records. No account, paid subscription or installer acceptance action was performed.
Use of the existing toolchain and the staged official SDK remains subject to their
applicable terms; this is not an assertion that use has no contractual conditions.

## Distribution route and conditions

The Community agreement permits distribution of listed object-code files,
including onward application distribution, subject to its conditions: significant
application functionality, protective downstream terms and specified restrictions.
Preview/unreleased files are excluded. Original notices must be preserved, and
Microsoft code must not be relicensed as project GPL code. The ordinary runtime
end-user licence's permission to install/use is not itself a redistribution grant.
See [Microsoft's redistribution guidance](https://learn.microsoft.com/en-us/cpp/windows/redistributing-visual-cpp-files?view=msvc-170)
and [2026 distributable list](https://learn.microsoft.com/en-us/visualstudio/releases/2026/redistribution).

These are conditions to document, not a claim that every file found in a Python
wheel automatically has unrestricted redistribution rights. The official runtime
licence and VS developer redistribution terms are different documents.

## Actual b3 files and remaining evidence

The immutable b3 inventory records Python VCRUNTIME 14.42.34438, Qt/Shiboken MSVC
14.44.35211, the NumPy-renamed MSVCP 14.40.33810 and PyWinRT MSVCP 14.29.30157.
These came from installed packages/base Python, not one unified current redist
directory. The installed compiler redist is 14.51.36231. Exact old-version file
entitlement and downstream notice/terms coverage therefore still require review;
the existence of a current redist is not a retroactive proof for older wheel bytes.
File origin/version/signature evidence is kept separate from redistribution rights.

Two documented paths are available: prove the older file grants, or test a new
candidate using unmodified stable files from a clearly identified licensed redist
and retain its terms/REDIST evidence. Do not overwrite b3 or remove required runtime
files simply to make this list shorter. A user downloading the official runtime
directly is another route, with installation/offline/admin tradeoffs; it is not
silently substituted for our portable distribution.

## GPL interaction

An unmodified compiler runtime implementing standard C/C++ interfaces is a
candidate for GPLv3's section 1 System Library exception. This is a reasoned
per-component classification, not a blanket exception for all Windows DLLs.
The Microsoft proprietary runtime stays under its own terms. Qt, FFmpeg, OpenSSL,
OpenBLAS and Mesa are assessed separately. Document the applicable exception and
downstream terms before treating the whole binary release as cleared.

**Input from owner:** no private Microsoft credential or paid subscription is
needed for the current technical review. If the publisher relies on a personal
agreement, that agreement's applicability must be confirmed by its holder; an
automated scan cannot attest it. No purchase or account setup is initiated.

Local evidence additionally confirms stable Release channels, 12 runtime DLLs
without a prerelease PE flag, and a successful isolated source build with the
existing Community compiler and locally staged official SDK headers/link libraries.
The SDK is build-only and is not part of the application distribution.
