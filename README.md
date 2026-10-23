# Community Rule Sources

**English** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

This community-maintained repository distributes optional encrypted rule collections
through GitHub Releases for compatible readers, including KiokuYomi.

This is not an official KiokuYomi repository or an official rule channel for any app.
Community members create and submit these rules independently. KiokuYomi developers
do not review, endorse, or guarantee them, and the app does not bundle third-party websites.

This repository hosts no manga or video content. Only access content you are authorized
to use, and comply with applicable laws and service terms.

## Find and Import One Source

**[Browse individual sources (excluding adult-rated sources)](SOURCES.md)**

You do not need to add an entire collection. Open the directory and use your browser's
"Find in page" to search by name or rule ID. Right-click or long-press an "Import link",
copy its address, and paste it into a compatible reader's remote rule import screen.
Review the import preview before confirming. You can also download a version-pinned
`.kyyrule` file and import it manually.

Stable links point to the corresponding source package in the latest Release. Clicking
one may download a file directly; it does not promise one-click app installation or
automatic updates after installation. Directories are generated from published collections.
The regular directory includes mature-rated sources and is not an all-ages directory.

The [separate adult directory](docs/SOURCES_ADULT.md) is an opt-in page for users who
meet applicable age and legal requirements.

## Add a Collection Manually

Paste an HTTPS collection URL into KiokuYomi's rule collection or remote rule import
screen, review the import preview, and confirm only if you choose to proceed.

**General collection (excluding adult-rated sources):**

```text
https://github.com/manga-rule-community/sources/releases/latest/download/general.json
```

**Full collection (may include adult-rated sources; applicable age and legal requirements apply):**

```text
https://github.com/manga-rule-community/sources/releases/latest/download/all.json
```

Alternative GitHub raw collection URLs:

```text
https://raw.githubusercontent.com/manga-rule-community/sources/main/general.json
https://raw.githubusercontent.com/manga-rule-community/sources/main/all.json
```

## Compatibility

The existing `kiokuyomi-Community/sources` repository remains available as a compatibility
mirror. Both repositories distribute the same published encrypted rule packages.
Adding either collection is sufficient; you do not need both.

## Feedback and Removal Requests

Report version or import problems and removal requests through
[repository Issues](https://github.com/manga-rule-community/sources/issues).
Rights holders should identify the rule ID, the rights involved, and a verifiable basis
for the request. Do not post identity documents, account credentials, private materials,
or complete copyrighted works in a public Issue. Removals must also reach the upstream
release and relevant distribution channels, not just this README.

Use these rules only for content you are authorized to access. Encryption and separate
repositories do not replace authorization, copyright, or platform policy requirements.

## Development

See [Development and Maintenance](docs/DEVELOPMENT.md) for the distribution architecture,
release workflow, and local validation commands.
