# Security

Report a vulnerability through this repository's private vulnerability reporting
feature when available. Do not post credentials or exploit details in a public issue.

SkillFleet accepts public GitHub HTTPS sources, pins commits and trees, rejects
symlinks/submodules in Git trees, guards project paths and checks managed file hashes.
It does not execute upstream code while installing. These controls do not make
third-party instructions trustworthy; review upstream changes and inspect helpers
before an agent executes them.

There is no automatic merge or global upgrade. A project update requires a local
proposal and explicit apply command. Local edits block overwrites. Keep the normal
project Git history in addition to SkillFleet's local recovery snapshots.
