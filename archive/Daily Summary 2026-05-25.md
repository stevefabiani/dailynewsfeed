# Cobalt Shields - What We're Reading Today — 2026-05-25

**Compiled:** Mon, 25 May 2026 14:30:00 GMT
**Window:** Items published or updated after 02:30 on the previous day (Sunday, 24 May 2026)
**Source pool:** BBC, DW, France 24, NHK World, ABC Australia, CBC, Swissinfo, NPR, PBS NewsHour, Reuters, AP, AFP, The Conversation, ProPublica, CSMonitor, Al Jazeera English, The Guardian
**Sector focus:** healthcare · higher ed · government · K-12 · nonprofit

> Note: 24–25 May fell on the U.S. Memorial Day weekend, so original reporting in scope was light. Today's brief leads with two actively exploited threats with direct sector impact, plus a weekly threat roundup for breadth.

---

## 1. TrapDoor cross-ecosystem supply chain attack hits npm, PyPI, and Crates.io and poisons AI coding assistants

**Category:** Supply Chain Security · **Published:** Mon, 25 May 2026
**Link:** https://thehackernews.com/2026/05/trapdoor-supply-chain-attack-spreads.html
**Companion:** https://socket.dev/blog/trapdoor-crypto-stealer-npm-pypi-crates
**Source:** The Hacker News

Socket researchers disclosed TrapDoor, a coordinated supply chain campaign that planted more than 34 malicious packages across 384+ versions on npm, PyPI, and Crates.io to steal SSH keys, AWS credentials, GitHub tokens, browser data, and crypto wallets from developers. Most notably, the operators poisoned AI coding assistants by embedding zero-width-Unicode instructions in CLAUDE.md and .cursorrules files submitted via pull requests to popular projects including LangChain, LlamaIndex, and MetaGPT, tricking tools like Cursor and Claude Code into running a fake "security scan" that exfiltrates secrets. The technique extends supply chain risk from package installs to the AI agents now embedded in many development workflows. Healthcare, higher-ed, and government teams adopting AI-assisted coding should pin dependencies, review agent configuration files, and rotate exposed credentials.

---

## 2. Actively exploited Ghost CMS SQL injection (CVE-2026-26980) fuels large-scale ClickFix campaign hitting university portals

**Category:** Vulnerabilities · **Published:** Sun, 24 May 2026
**Link:** https://www.bleepingcomputer.com/news/security/ghost-cms-sql-injection-flaw-exploited-in-large-scale-clickfix-campaign/
**Companion:** https://blog.xlab.qianxin.com/ghost-cms-mass-compromised-via-cve-2026-26980-now-fueling-clickfix-attacks/
**Source:** BleepingComputer

Attackers are mass-exploiting CVE-2026-26980, an unauthenticated SQL injection flaw (CVSS 9.4) in the Ghost CMS Content API affecting versions 3.24.0 through 6.19.0 that exposes admin API keys. XLab researchers found the campaign has compromised more than 700 domains — including university portals, media outlets, and SaaS and fintech firms — by stealing API keys and bulk-injecting malicious JavaScript that serves fake Cloudflare "ClickFix" prompts tricking visitors into pasting attacker commands into Windows. Administrators running Ghost should upgrade immediately, rotate all Ghost Admin and Content API keys and admin credentials, and audit posts for injected loader scripts.

---

## 3. Security Affairs weekly roundup: Drupal KEV exploitation, Laravel-Lang and Megalodon supply chain attacks, and AI bug-hunting fallout

**Category:** Weekly Roundup · **Published:** Sun, 24 May 2026
**Link:** https://securityaffairs.com/192586/hacking/security-affairs-newsletter-round-578-by-pierluigi-paganini-international-edition.html
**Companion:** https://securityaffairs.com/192598/malware/security-affairs-malware-newsletter-round-98.html
**Source:** Security Affairs

Security Affairs' May 24 international newsletter rounds up the week's top threats, including active exploitation of the Drupal Core SQL injection (CVE-2026-9082) now in CISA's Known Exploited Vulnerabilities catalog, the Laravel-Lang and Megalodon software supply chain campaigns, and the patch-management strain created by AI-assisted vulnerability discovery. It is a useful weekly scan for healthcare, higher-ed, government, and nonprofit IT teams tracking the fast-moving supply chain and exploitation landscape.
