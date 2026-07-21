# Getting Bailey in front of friends & family

You have two decisions to make first, then pick a hosting option.

## 1. Which mode?

| Mode | What friends can do | Cost | Needs |
|---|---|---|---|
| **Demo** | Click through two built-in sample offers (a weak DSO offer and a strong private-practice one) and the compare view | **$0** | nothing — just set `BAILEY_DEMO=1` |
| **Real** | Upload *their own* contracts and get a real Claude analysis | ~a few cents to ~$0.30 of Anthropic API per review | your `ANTHROPIC_API_KEY` |

**Start with Demo mode to get feedback on the *experience* for free.** Switch to
Real mode (add your API key) once you want people analyzing their own offers.

## 2. Protect the link (Real mode)

A public URL running your API key means anyone with the link can spend your
Anthropic credits. Set a shared password so only people you give it to can use it:

- Set the env var `BAILEY_PASSWORD` to any phrase (e.g. `cedar-park-2026`).
- The browser shows a one-time login prompt — friends enter **any username** and
  that password.
- Leave `BAILEY_PASSWORD` unset for a fully open link (fine for Demo mode).

---

## Option A — Render (recommended: a real link, always on)

Gives you a permanent `https://bailey-xxxx.onrender.com` URL. Free tier is enough
for feedback (the app sleeps after ~15 min idle and takes ~30–60 s to wake on the
next visit — normal for free hosting).

1. **Push the code to your GitHub** (already done if this repo is on GitHub).
   Note the branch — you can deploy `main` or this feature branch.
2. Go to **[render.com](https://render.com)** and sign up (free, GitHub login).
3. Click **New ▸ Blueprint**, authorize GitHub, and pick this repository.
   Render finds `render.yaml` and sets everything up automatically.
4. When prompted for the environment variables, enter:
   - **`ANTHROPIC_API_KEY`** — your key (or leave blank for Demo).
   - **`BAILEY_DEMO`** — `1` for Demo mode, or leave blank for Real mode.
   - **`BAILEY_PASSWORD`** — a shared password (recommended for Real mode).
5. Click **Apply**. First build takes a few minutes. When it's live, Render shows
   your URL — share that with friends.

To change a setting later: Render dashboard ▸ your service ▸ **Environment** ▸ edit
the variable ▸ save (it redeploys automatically).

> Get your Anthropic API key at **console.anthropic.com** ▸ API Keys. Set a
> monthly spend limit there too — cheap insurance while you gather feedback.

## Option B — Quick share from your own computer (a live session)

Best when you want to sit with someone (or screen-share) for 20 minutes rather
than host a permanent site. Your laptop must stay on and running.

```bash
cd bailey
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # or: export BAILEY_DEMO=1
uvicorn app:app --host 0.0.0.0 --port 8000
```

Then, in a second terminal, open a public tunnel to it:

```bash
# Cloudflare Tunnel — no signup needed
cloudflared tunnel --url http://localhost:8000
# (install once: `brew install cloudflared` on Mac)
```

It prints a temporary `https://…trycloudflare.com` link. Share it; it lasts until
you stop the command. (ngrok works the same way if you prefer.)

---

## Which should I pick?

- **Want people to try it on their own time, from a link you text them?** → Render.
- **Want to watch someone use it and take notes right now?** → the tunnel.

Either way: **deploy in Demo mode first**, get reactions to the flow and the
report, then flip on your API key + password when you're ready for real contracts.
