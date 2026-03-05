---
name: nanoclaw-login
description: >
  Helper skill for authenticating NanoClaw to WhatsApp. Since NanoClaw
  separates the auth process from the main process, this skill automatically
  runs `npm run auth`, waits for the QR code, and guides the user. It also
  handles the common QR code timeout or stream (515) errors.
  Trigger: "login nanoclaw", "auth whatsapp", "scan qr nanoclaw", "konek whatsapp nanoclaw".
category: App-Specific
---

# NanoClaw Login Helper

## Why this skill exists
NanoClaw's main process (`npm start`) instantly crashes if credentials are not present. Users must run a dedicated auth script (`npm run auth`) to view the QR code in the terminal.

## Execution Steps

### Step 1 — Check Directory
Must be run inside the NanoClaw project folder.
```bash
cd ~/Projects/nanoclaw
```

### Step 2 — Clean Existing Credentials (Optional but recommended for fresh auth)
If the user is trying to switch numbers or fix a hung state:
```bash
# This cleans stale files from a previous failed auth
npm run auth -- --clean
# OR manually:
rm -rf store/auth/ store/qr-data.txt store/auth-status.txt
```

### Step 3 — Start Auth Script
Run the dedicated authentication script:
```bash
npm run auth
```

### Step 4 — Guide the User
Once the ASCII QR Code appears in the terminal (like it did in your previous command), provide these exact instructions to the user:

1. Open **WhatsApp** on your phone.
2. Tap the **3-dot menu** (Android) or **Settings** (iOS).
3. Select **Linked Devices** (Perangkat Tertaut).
4. Tap **Link a Device**.
5. Scan the QR code currently shown in the terminal.

> **⚠️ WARNING:** The QR code expires in about 60 seconds. If they get a `✗ QR code timed out` error, tell them everything is fine and just re-run Step 3.

### Step 5 — Verify Success
Wait for the terminal to print:
`✓ Successfully authenticated with WhatsApp!`
(The script will then exit automatically with code 0).

Only **after** Step 5 is successful should the user be told to run `npm start`.

---

## Known Errors & Fixes
- **Error:** `WhatsApp authentication required. Run /setup` during `npm start`
  **Fix:** Run this skill (`npm run auth` instead).
- **Error:** `✗ QR code timed out`
  **Fix:** The user was too slow to scan. Just re-run `npm run auth` and tell them to prepare their phone camera beforehand.
- **Error:** `⟳ Stream error (515) after pairing`
  **Fix:** Normal Baileys websocket glitch. The script auto-reconnects, just wait.
- **Error:** `✗ Connection failed. Please try again.`
  **Fix:** Usually network/firewall issue blocking Baileys, or banned number.
