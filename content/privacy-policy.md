# Titan X Privacy Policy (DRAFT)

Draft of 2026-11-17. Not reviewed by counsel. Not committed. Replace [brackets] before publishing.
Things that are planned but not built are marked **(planned)**.

**Who we are.** Titan X is made by [legal entity], [address]. Contact: [privacy email].

## The short version

- Titan X keeps your training data **on your phone**.
- We do not sell data, show ads, or track you across apps or websites.
- Apple Health data is read only, stays on your phone, and is never used for advertising.
- **(Planned)** A gym can choose to send finished session records to its coach's computer through a temporary cloud store. The store is emptied after each pickup.

## What the app uses, and where it goes

**Apple Health (read only).** With your permission, Titan X reads:
- heart rate, resting heart rate, heart rate variability, one-minute heart rate recovery and VO2 max;
- sleep, steps and workouts;
- active and resting energy, weight and height.

It shows your trends on your phone. It never writes to Apple Health. Health data is not sent to us, your gym or anyone else. You can turn access off at any time in Settings > Health.

**Heart rate and motion sensors (Bluetooth).** During training the app connects to the team's sensors (Polar Verity Sense, SensWear boards). It uses them to show effort zones and to count head contacts. Raw sensor recordings and the sensor's stored motion log are saved on the phone that ran the session.

**What you type.** Names, profiles, plans, check-ins (readiness, fatigue, illness signs, pain areas), coach notes and holds are kept in the app's file on your phone. The file is protected by iOS encryption and unlocked after the first unlock following a restart.

**The assistant ("Ask").**
- By default it runs on your phone using Apple's on-device model, and your questions do not leave the phone.
- If your gym turns on its own assistant server, your question is sent to that server. Athlete names are replaced with random codes first, and the server receives only the facts it needs to answer. You must agree first, and health details stay off unless you choose them.

**Phone use and sleep estimate (Screen Time).** This is only on builds where Apple has approved it. If you turn it on, the app records when your total phone use crossed 5-minute steps, to estimate when you slept. It never learns which apps or websites you used. The data stays on the phone.

**Sharing a records file.** If you export a `.titanx` file and send it (for example by AirDrop), the person you send it to receives what's in it.

## (Planned) Session data return

So that coaches can review sessions on the gym's computer, the app will be able to upload finished session records to a cloud database run by [provider, likely Supabase, region].

- **What:** session records (attendance, minutes, effort ratings, sensor heart rate and contact counts), check-ins, and the athlete and coach names and ids needed to file them.
- **Not included:** Apple Health data, Screen Time data and raw sensor files, unless we say otherwise here first.
- **How long:** the gym's computer downloads the records and then deletes them from the cloud database. The target is that nothing stays in the cloud beyond [N days].
- **Who can see it:** only the gym's staff accounts. [Provider] processes it for us under its data processing terms.
- **Security:** encrypted in transit (TLS) and at rest by the provider. [Access control details.]

## Children

Some athletes may be under 18. A parent or guardian must agree before a minor's data is used by the assistant or by the data return. [Age threshold and verification: counsel to confirm.]

## Your choices

You can:
- turn off Apple Health, Bluetooth or Screen Time access in iOS Settings;
- delete the app to remove all data stored on the phone;
- ask your gym to delete records it holds. **(Planned)** You can also ask us at [privacy email] to delete data in the cloud store.

## Changes

We will update this page and the date above when anything changes, including when the data return goes live.
