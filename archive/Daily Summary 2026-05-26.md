# Cobalt Shields - What We're Reading Today — 2026-05-26

**Compiled:** Tue, 26 May 2026 14:30:00 GMT
**Window:** Items published or updated after 02:30 on the previous day (Monday, 25 May 2026)
**Source pool:** BBC, DW, France 24, NHK World, ABC Australia, CBC, Swissinfo, NPR, PBS NewsHour, Reuters, AP, AFP, The Conversation, ProPublica, CSMonitor, Al Jazeera English, The Guardian
**Sector focus:** healthcare · higher ed · government · K-12 · nonprofit

> Note: The brief leads with a freshly disclosed, actively exploited flaw in an education learning management system, followed by two end-user/identity security items with broad sector impact.

---

## 1. Hard-coded ASP.NET keys in KnowledgeDeliver LMS (CVE-2026-5426) exploited to deploy Godzilla web shell and Cobalt Strike at schools

**Category:** Vulnerabilities · **Published:** Tue, 26 May 2026
**Link:** https://thehackernews.com/2026/05/knowledgedeliver-lms-flaw-exploited-to.html
**Source:** The Hacker News

Google Mandiant disclosed that attackers are exploiting CVE-2026-5426 (CVSS 7.5), a hard-coded ASP.NET machine-key flaw in Digital Knowledge's KnowledgeDeliver learning management system that enables unauthenticated remote code execution through ViewState deserialization. After gaining access, the operators drop the Godzilla web shell and tamper with site JavaScript to show fake "security plugin" prompts that ultimately deliver a Cobalt Strike Beacon to visitors. KnowledgeDeliver is widely deployed across educational institutions, making this a direct threat to K-12 and higher-ed IT teams. Administrators should upgrade to the patched release (post–February 24, 2026), replace any shared machine keys with unique secrets, and deploy endpoint monitoring.

---

## 2. Anthropic's restricted Claude Mythos model spotted heading to Claude Code

**Category:** AI Security · **Published:** Mon, 25 May 2026
**Link:** https://www.bleepingcomputer.com/news/artificial-intelligence/anthropics-restricted-claude-mythos-model-may-be-coming-to-claude-code/
**Source:** BleepingComputer

BleepingComputer reports that Anthropic appears to be preparing a public rollout of Claude Mythos, the frontier model announced in April 2026 as a restricted system because it can autonomously develop professional-grade cyberattacks. Users briefly spotted a "claude-mythos-1-preview" toggle in Claude Code before it was removed, and the model has also surfaced in Claude Security. Mythos is the engine behind Anthropic's Glasswing program, which surfaced more than 10,000 high- and critical-severity vulnerabilities in its first month. IT leaders evaluating AI-assisted development should weigh both the defensive upside and the dual-use risk as these capabilities reach mainstream tooling.

---

## 3. FBI warns of Kali365 phishing-as-a-service abusing OAuth device codes to hijack Microsoft 365 accounts

**Category:** Phishing · **Published:** Mon, 25 May 2026
**Link:** https://www.bleepingcomputer.com/news/security/fbi-warns-of-kali365-phishing-service-targeting-microsoft-365-accounts/
**Source:** BleepingComputer

The FBI issued an alert about Kali365, a phishing-as-a-service platform that emerged in April 2026 and is sold via Telegram to compromise Microsoft 365 and Entra accounts without stealing passwords or intercepting MFA codes. It abuses Microsoft's legitimate OAuth 2.0 device-authorization flow — tricking victims into entering an attacker-generated device code and completing MFA — to hand the attacker a full-access token, and offers an adversary-in-the-middle "Cookie Link" mode to capture authenticated sessions. Attackers have accessed mailboxes and created hidden inbox rules to mask activity; similar kits like EvilTokens and Tycoon2FA use the same technique. The FBI urges organizations to restrict or block device-code authentication via Conditional Access, audit existing device-code usage, and report incidents to IC3.
