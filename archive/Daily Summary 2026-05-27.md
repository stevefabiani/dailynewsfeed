# Cobalt Shields - What We're Reading Today — 2026-05-27

**Compiled:** Wed, 27 May 2026 14:30:00 GMT
**Window:** Items published or updated after 02:30 on the previous day (Tuesday, 26 May 2026)
**Source pool:** BBC, DW, France 24, NHK World, ABC Australia, CBC, Swissinfo, NPR, PBS NewsHour, Reuters, AP, AFP, The Conversation, ProPublica, CSMonitor, Al Jazeera English, The Guardian
**Sector focus:** healthcare · higher ed · government · K-12 · nonprofit

> Note: Today's brief leads with a freshly patched SharePoint RCE that affects on-premises deployments across all target sectors, followed by an Iranian espionage campaign touching education and government, a new Defender containment capability, and a foreign-suspected national-register breach in Lithuania.

---

## 1. Microsoft patches SharePoint RCE flaw CVE-2026-45659 across on-premises Server versions

**Category:** Vulnerabilities · **Published:** Tue, 26 May 2026
**Link:** https://thehackernews.com/2026/05/microsoft-patches-sharepoint-rce-flaw.html
**Source:** The Hacker News

Microsoft released a fix for CVE-2026-45659 (CVSS 8.8), a deserialization-of-untrusted-data flaw in on-premises SharePoint Server that lets an authenticated user with only Site Member permissions execute code remotely — no administrator rights required. The bug affects SharePoint Server Subscription Edition, SharePoint Server 2019, and SharePoint Enterprise Server 2016. Microsoft rates it "less likely to be exploited" and no in-the-wild attacks have been reported, but SharePoint flaws have been repeatedly weaponized, so administrators of self-hosted farms should patch promptly. On-prem SharePoint remains common across higher-ed, healthcare, and government, making this a priority update for those IT teams.

---

## 2. Iranian group MuddyWater uses signed-binary DLL side-loading to hit education and public-sector targets across nine countries

**Category:** Threat Intelligence · **Published:** Tue, 26 May 2026
**Link:** https://thehackernews.com/2026/05/muddywater-uses-dll-side-loading-in.html
**Source:** The Hacker News

Researchers detailed a refined MuddyWater (Seedworm) espionage campaign in which the IRGC-linked Iranian group abused legitimately signed Fortemedia and SentinelOne binaries to side-load malicious DLLs, then ran Node.js-launched PowerShell for reconnaissance and credential theft via the ChromElevator tool. Nine organizations across four continents were hit — spanning education, public sector, financial services, industrial manufacturing, and professional services — with attackers dwelling about a week inside one South Korean victim and staging stolen data on the public sendit.sh service. The operators showed markedly improved operational security over prior campaigns. Education and government IT teams should hunt for anomalous use of signed vendor binaries and unexpected Node.js or PowerShell activity. Companion analysis: https://www.securityweek.com/iranian-apt-targets-aviation-software-companies-with-updated-tools/

---

## 3. Microsoft Defender for Endpoint can now automatically isolate compromised devices

**Category:** Endpoint Security · **Published:** Tue, 26 May 2026
**Link:** https://www.bleepingcomputer.com/news/microsoft/microsoft-defender-can-now-automatically-isolate-hacked-endpoints/
**Source:** BleepingComputer

Microsoft is previewing an automatic device-isolation capability in Defender for Endpoint that, as part of "automatic attack disruption," cuts a suspected-compromised workstation off from the network while keeping it connected to the Defender service for continued monitoring. The feature aims to contain threats and limit lateral movement without waiting for analyst action, and security teams can manually release devices after investigating through the device inventory. It currently works only on onboarded end-user workstations and remains in preview. The change is relevant to resource-constrained healthcare, education, and government SOCs weighing automated containment against the risk of disrupting legitimate endpoints.

---

## 4. Lithuania suspects foreign actor behind leak of 600,000+ national register records

**Category:** Major Breach · **Published:** Tue, 26 May 2026
**Link:** https://www.securityweek.com/lithuania-suspects-foreign-involvement-in-data-leak-of-over-600000-national-register-entries/
**Source:** SecurityWeek

Lithuania's State Enterprise Centre of Registers disclosed that more than 600,000 entries from the country's real-estate and legal-entity registers were accessed using stolen credentials belonging to institutions authorized to query the data. Officials suspect a foreign state — an opposition politician pointed to Russia without providing evidence — amid Lithuania's standing as a frequent target of hybrid operations against Europe. Authorities have blocked the suspected accounts and now require credential updates for register access, and the agency's head resigned over the incident. The breach is a reminder for government data custodians that authorized third-party credentials are a prime avenue for large-scale register compromise.
