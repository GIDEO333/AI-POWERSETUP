---
name: sandbox-executor-setup
description: Merancang wrapper Docker MicroVM berlapis timeout guard untuk mengamankan eksekusi AI CLI otonom dari pengerutan sistem host, hang terminal, dan bahaya filesystem.
category: Ops
---

# Sandbox Executor Setup (Meta-Skill)

## Tujuan
Mengonversi eksekutor CLI lokal yang berbahaya (seperti `claude` CLI dengan flag bypass) ke dalam ekosistem *MicroVM* terisolasi yang kebal dari *error loop* dan ancaman perusakan OS.

## Kapan Menggunakan
- Ketika Anda ingin memberikan izin otonom (tanpa konfirmasi manual) kepada AI agent untuk mengeksekusi *tools* bash.
- Saat Anda menyusun skrip *shell* untuk dioperasikan oleh bot saat Anda tertidur/jauh dari keyboard.

## Prinsip Desain (Agnostik Bahasa)
Desain pengaman AI ini **berlaku universal** entah AI sedang men-*deploy* kubernetes, menulis Python, ataupun membangun aplikasi React:
1. **Host Isolation:** Proses AI tidak akan pernah dipanggil dari *shell* OS murni. Semua harus dialihkan melalui *hypervisor* ringan atau Docker.
2. **Deterministic Termination:** Jangan pernah meyakini bahwa AI akan mengakhiri aplikasinya secara "*clean*". Wajib sediakan "Kampak Waktu" (Hard Timeout Guard) pada lapisan pembungkus OS.

## Architecture Blueprint (Standar Prosedur)

Ketika Anda ditugaskan membuat *Bash Wrapper* untuk agent:

### 1. Ubah Executable
Jangan pernah menggunakan perintah *native* seperti:
`ai-cli --skip-permissions "Tugas Anda..."`

Selalu bungkus ke dalam Docker VM bayangan (Sandboxing) dengan pembatasan jaringan (jika diperlukan) dan pe-(*mount*)-an root ke *Current Working Directory* saja.
Gunakan komando yang setara dengan:
`docker sandbox run ai-cli -- "Tugas Anda..."`

### 2. Tanamkan The Time-Bomb (Hard Limit)
Di lapis terluar Bash, implementasikan utilitas `timeout` standar POSIX Unix untuk mengirim sinyal SIGKILL absolut bilamana agent terjebak memanggil proses *blocking* seperti menghidupkan *web server* atau *daemon* jaringan.
Contoh:
`timeout -k 30s 900s docker sandbox run ai-cli ...`

Ini memastikan, sesulit apa pun logika agen memutar balik *error*, di menit ke-15 mesin eksekusi tersebut terbunuh paksa tanpa meninggalkan *zombie process* pemakan memori di dalam OS.
