# Repatrol Demo Voiceover (ElevenLabs TTS)

## Settings
- **Voice:** Pick a calm, confident male or female voice (e.g. "Adam", "Rachel", or "Antoni")
- **Stability:** 0.50
- **Clarity + Similarity Enhancement:** 0.75
- **Style:** 0 (neutral — no dramatic flair)
- **Speed:** Slightly slow

## Script

Repatrol. An autonomous swarm of AI agents that visually test your games and web apps, finding bugs so your QA team doesn't have to.

Manual visual testing is slow, expensive, and error-prone. UI glitches and gameplay crashes often slip into production because human testers can't click every button on every release. 

Here's how Repatrol changes the game.

We deploy a swarm of specialized agents. An Explorer Agent systematically navigates the interface using vision models. When it detects an anomaly, a Bug Hunter Agent takes over to verify the issue. 

Finally, a Reporter Agent documents the exact steps to reproduce it and automatically files a ticket.

Let me show you a live run. The agents are launching a headless browser now.

Watch the coverage map. The Explorer Agent is autonomously clicking through the menus—"Start," "Boost," "Fire." It's analyzing screenshots in real-time to understand the state of the application. 

Suddenly, it triggers an unhandled exception in the UI.

The Bug Hunter confirms the crash. Instantly, the Reporter Agent kicks in. 

It compiles the visual evidence, maps the exact sequence of actions that caused the failure, and drafts a complete Markdown issue file, ready to be pushed directly to GitHub. 

Sixty-six percent functional coverage, one critical bug found, and zero human intervention required. 

Built for the Microsoft AI Dev Days Hackathon twenty twenty-six. Thank you for watching.
