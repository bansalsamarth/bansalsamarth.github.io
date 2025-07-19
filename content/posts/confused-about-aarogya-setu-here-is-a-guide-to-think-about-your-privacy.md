---
category: personal
date: '2020-05-17'
published: true
slug: confused-about-aarogya-setu-here-is-a-guide-to-think-about-your-privacy
title: Confused about Aarogya Setu? Here is a guide to think about your privacy
---

Many are concerned that [Aarogya Setu, India’s contact tracing app, is a privacy disaster,](https://www.bbc.com/news/world-asia-india-52659520) a mass surveillance project masquerading as a tool for public health interventions.

Well, the privacy concerns are obvious: the purpose of the app is to track you. It asks you for the most sensitive information that a smartphone can collect: your location. The government wants you to give access to your location all the time—every fifteen minutes to be precise. Every move will be tracked. Bluetooth access allows the app to keep a log of every person you came in close contact with—who also has the app installed. This helps in contact tracing while GPS data aids in identifying disease hotspots. The government won’t pull in the data until it is necessary, the privacy policy says, and claim that they care about privacy.

I [explained this, and more about the idea behind the app, in *Mint,*](https://www.livemint.com/news/india/india-is-pinning-hopes-on-apps-in-virus-fight-11586447095280.html) a week after the app was launched in April. I also compared the app with home quarantine monitoring apps that various state governments had built, specifically looking at Maharashtra government’s Mahakavach. I wrote:

> While the material goal of both Aarogya Setu and Mahakavach is to fight the pandemic, the philosophical difference could not be more different. Mahakavach is built on a social contract where the state believes that citizens can’t be trusted while the success of Aarogya Setu is fundamentally dependent on the citizens trusting the state, installing the app and sharing sensitive data. Which way will India go in the weeks ahead?

It is now clear the direction India has taken: my analysis didn’t stand the test of the time as the Government of India is on path to make Aarogya Setu *mandatory*—the state will coerce the citizens to install the app. They will face consequences if they don’t, from restricting movement to jail term.

This is obviously problematic, irrespective of whether the app has privacy concerns or not: coercion is a powerful tool for harassment in the hands of law enforcement.

Despite all that, I think we are missing on the nuance on privacy concerns.

### Privacy policy and trust

Before I get there, I want to say one more thing to set the context. And that is about the app’s privacy policy: it has some really good features—like data stays on the phone until you come in close contact with covid positive patient or you test positive—but I don’t trust it.

Because there are no *technical safeguards*. Think of it as the difference between WhatsApp and Facebook messenger. Both are owned by Facebook. For messenger, the company claims they don’t look at private messages. They don’t, but they can. That is not the case with WhatsApp: the company, even if it wants, even if the government instructs them to, they can’t look at the messages because they are end-to-end encrypted.

That’s what I mean by technical safeguards, or constraints. When they are absent, we have to trust the app developers to not misuse our data, and hold on the promise they are making in the privacy policy. I don’t trust the Indian government to protect my privacy. Zero trust. Plus, we don’t even have a data protection law, and the one that was tabled in the Parliament, [does not restrict government’s power over citizen’s private data.](https://www.livemint.com/news/india/big-brother-on-top-in-data-protection-bill-11576164271430.html)

That means: when I use the app, I do so under the assumption that *nothing in the privacy policy will hold*. I want to be prepared for the worst case scenario—even if there is a less than 1% chance of that happening.

So I am assuming that the government will have access to my data at its whim—whenever it wants—and at least one copy of the data would exist forever, that it won’t be deleted, even though the policy says data would be deleted after 180 days.

### Will I use the app?

Yes, I will—despite all the concerns. But in a limited way. There aren’t simple yes/no answers to the question “will this technology violate my privacy?”. You need to ask specific questions—it’s called [threat modelling in digital security paradigm](https://ssd.eff.org/en/module/your-security-plan)—to understand what data we want to protect, from whom, the risks of failing to protect it, the likelihood that it needs to be protected, and assess the trouble we are willing to go through to protect our information.

Note that the explanation that follows is my view as a user of the app and *what it means for me, personally.*

### What data does Aarogya Setu collect?

As of May 17:

**1. Basic demographic information**: name, mobile number, age, gender, profession. This information goes to a government server and what you get in return is a Device ID — DiD — number that is used in all future interactions.

***Concerns sharing this with government:*** Not much. Okay sharing this.

**2. Data collected via self-assessment test:** The app has a quiz which asks you basic questions like symptoms you are experiencing, health problems in the past, international travel history etc. You have to select from options given by the app. They have basically converted instructions into multiple choice questions which one can use to assess their risk — which you can easily do without taking the quiz.

***Concerns sharing this with government:*** I gain nothing insightful by using this service — so I won’t use this feature. But in any case, I don’t mind sharing this. I know exactly the information I am entering here, and am okay with it.

**3. Contact data:** People I have come in close contact with, including the duration of contact, distance and location of contact. This is the whole point of a contact tracing app. When I come in contact with another user of the app, both of our apps will exchange their DiDs. If the other person tests positive, this information will be uploaded to the server.

**4. Location Data:** The app continuously collects my location data at 15 minute intervals and stores it on my phone. It uploads this information to the server only if I test positive or the self-assessment test says I am “at risk” or “unwell”.

***Concerns sharing this with government for (3) and (4):*** I have hesitation in sharing this data all the time — especially location — but I also want to be alerted in case I come in contact with a covid-19 positive patient.

While I have my doubts whether the app will work or not, I am open to be a part of this experiment. I am willing to give up some private information for potential public health gains. The larger point here is rejection of privacy absolutism. Privacy is not an end in itself. My default state remains more privacy everywhere, but I do evaluate trade-offs in cases where I need to share private information for another goal I care about—here, public health.

If in weeks to come it becomes clear that the app doesn’t work as intended, there is no case to surrender any information whatsoever. To be sure, I am strictly against location tracking, and only making an exception right now because of the pandemic and the unprecedented circumstances we are living through.

### So how will I use it?

Fairly simple:

**Restrict location access through permissions:** Smartphone is one of the most advanced surveillance tools. But fortunately, we have smartphone permissions, which introduces barriers for app developers to access specific parts of your phone data. Both iOS and Android offer its users three levels of location access to any app: “Allow all the time”, “Allow only while the app is in use”, “Deny”. Aarogya Setu requests its user to set the access level to “Allow all the time”, which I would never enable. Never—for any app whatsoever. 

So step one for me is to set location access to “Allow only while the app is in use”.

**Be conscious when you want the app to collect data:** I will selectively give access to my location and Bluetooth to the app for contact tracing purposes. This means I need to be very cautious about the app all the time. I am willing to take that cognitive burden for the time being. If and when I go to the market—or any crowded public place for that matter—and I come in contact with a covid infected patient, I do want to be informed about that interaction.

That’s what I hope to gain from the app, and in return, I am okay letting the government know which market I visited, what route I took, with whom I went and when—all the information I would never want anyone else to know in normal circumstances. This is the trade-off I am making. Give data, but not all the time.

That’s it. This is how I plan to use Aarogya Setu: totally aware of the information I will share, recognising the risks associated with it and doing so for a perceived gain.

I want to especially stress here on one point. Unlike other mass surveillance technologies—CCTV cameras and location tracking via telephone metadata, for instance—where I can do little or nothing to not be surveilled, I have full control with Aarogya Setu. Even if the government makes it compulsory, as it is doing now, at any point, as per my own whim, I can just switch off the permissions, and stop sharing data with the government. This decentralised model of surveillance leaves some power with the citizens.

### Other concerns

**1. Can Aarogya Setu access any information beyond what it claims?** No. It is important to note that the *only permission* that Aarogya Setu requests for is your location access. That’s it. Without explicitly asking for any other permission, it can’t access any other data from my phone. It is technically not possible. Stressing this because some friends were worried about that possibility: the app can’t access your photographs, contacts, messages etc. (It can know, however, all the other apps on your phone — which is a bit creepy, yes!)

**2. What about**[**issues flagged by ethical hacker Elliot Anderson**](https://medium.com/@fs0c131y/aarogya-setu-the-story-of-a-failure-3a190a18e34)**?** Again, let me answer this for myself. The main issue Anderson flagged was the “ability to know who is sick anywhere in India”.

The concerns is based on a feature of Aarogya Setu that allows you to choose a radius—500m, 1km, 2kms, 5kms or 10kms—and know how many covid positive / unwell patients reside in that area. Anderson claims he was able to change the geo-location and find out how many positive people are there. For instance, one person near the Indian Army Headquarters was covid positive, Anderson found.

Well, I don’t see much of a problem here (many disagree). One can find the same information by going to that spot, open the app and get that information. So it is not a data breach so to say.

Anderson takes this further and says that using triangulation, an “attacker can get with a meter precision the health status of someone”. But as [WIRED pointed out,](https://www.wired.com/story/india-covid-19-contract-tracing-app-patient-location-privacy/) “the triangulation would also be most effective when a suspected Covid-19 positive person is the only reported case in roughly a kilometer radius”.

I am not too convinced that this is a major lapse. Generally speaking, I actually like this feature. In Delhi, for instance, the state government is concealing data, and for many days, didn’t even share district-wise breakup of covid cases. In that context, information from the app can help me make make everyday decisions on which areas are safe and which are not. A few days ago, the app told us that there are ten covid positive patients around my house (500m). We were alert, and next morning, we learnt that the virus had reached my own locality.
