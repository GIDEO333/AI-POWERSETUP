# 🛑 Panduan Bertahan Hidup Agent: macOS Sandboxing & EPERM Hell

Dokumen ini menjelaskan fenomena di mana Anda sebagai System Owner bisa melakukan segalanya secara normal di Terminal, namun AI Agent yang berjalan di VSCode/Cursor terus menerus menabrak tembok `EPERM (Operation not permitted)`.

## 1. Ilusi Kepemilikan (Ownership Illusion)
Agent sering mendiagnosis `EPERM` sebagai kegagalan `chmod` atau file yang dimiliki oleh `root`. Kenyataannya, **semua file sudah milik user Anda (`gideonthirtytres`)**, namun macOS App Sandbox yang dengan paksa meredam Agent karena ia berjalan sebagai *child process* dari IDE yang dicurigai sistem.

## 2. Sang Pelaku Utama (The Hidden Culprits)

### A. ACL (Access Control List) Gembok Tersembunyi
macOS sering secara berlapis menambahkan Access Control List (ACL) pada Home Directory (`~`), `~/.npm/`, dan `~/Library/Caches/`.
- **Bentuknya:** `0: group:everyone deny delete`
- **Efeknya:** Npm, Playwright, atau tool apa pun yang mencoba membuat file `temp` lalu menghapusnya (`rmdir` / `unlink`) akan diblokir oleh OS, meski folder itu milik user asli.
- **Gejala Palsu:** Npm akan berteriak "Your cache folder contains root-owned files" (ini halusinasi Npm).
- **The Golden Fix Command:**
  Jalankan perlahan di Terminal asli (bukan Agent Bash):
  ```bash
  sudo chmod -RN ~/.npm ~/Library/Caches ~/.config
  # Atau untuk menyapu bersih semua gembok di Home (Hati-hati):
  # sudo chmod -RN ~
  ```

### B. Korupsi macOS Keychain (GitHub CLI Auth Loop)
Saat Agent melakukan autentikasi (`gh auth login`) lalu mentok di pesat EPERM, sering kali OSX diam-diam memunculkan dialog GUI *di layar Mac*: **"Keychain 'login' cannot be found to store GIDEO333"**.
- Token API gagal tersimpan ke `~/.config/gh/hosts.yml` karena korupsi Keychain.
- **The Golden Fix:** Klik "Reset to Defaults" pada popup UI Mac yang muncul, agar Mac membuat ulang brankas password yang rusak. Atau, gunakan Personal Access Token (PAT) *no expiration*.

## 3. Playwright EPERM Loop (The 2026 Bypass)
Ketika menginstal Playwright CLI secara global, Agent akan selalu dihantam EPERM saat menginstal *Chrome for Testing* ke dalam `~/Library/Caches/ms-playwright`.

**SOP Resmi Instalasi Playwright Agent di Mac:**
1. Hindari `npm install -g`. Gunakan selalu `npx`.
2. Gunakan Environment Variables untuk membajak lokasi instalasi browser ke folder lokal project guna menghindari `~/Library/Caches` sepenuhnya:
   ```bash
   PLAYWRIGHT_BROWSERS_PATH=./.browsers npx --cache /tmp/npmcache -y @playwright/cli@latest install-browser --browser chrome
   ```

*(Dikompilasi dari post-mortem debugging Switchboard MCP Playwright CLI - Maret 2026)*
