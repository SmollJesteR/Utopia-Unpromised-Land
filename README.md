# LAPORAN TUGAS BESAR

## PEMROGRAMAN BERORIENTASI OBJEK

# Utopia Unpromised Land

<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>
<br>

## KELOMPOK 2

<br>
<br>
<br>

### PROGRAM STUDI TEKNIK INFORMATIKA

### FAKULTAS TEKNOLOGI INDUSTRI

### INSTITUT TEKNOLOGI SUMATERA

### 2025

# DAFTAR ISI

A. [DESKRIPSI PENUGASAN](#deskripsi-penugasan)  
B. [NAMA GAME](#nama-game)
C. [KATEGORI GAME](#kategori-game)
D. [ENTITAS](#entitas)
E. [DESKRIPSI GAME](#deskripsi-game)
F. [TAMPILAN GAME](#tampilan-game)
G. [KELAS](#kelas)
H. [OBJEK](#objek)
I. [ENKAPSULASI](#enkapsulasi)
J. [PEWARISAN](#pewarisan)
K. [POLIMORFISME](#polimorfisme)
L. [ABSTRAKSI](#abstraksi)
M. [PENANGANAN KESALAHAN](#penanganan-kesalahan)
N. [GRAPHICAL USER INTERFACE](#graphical-user-interface)
O. [DIAGRAM UNIFIED MODELING LANGUAGE](#diagram-unified-modeling-language)
P. [KODE](#kode)
Q. [LAMPIRAN](#lampiran)

# DESKRIPSI PENUGASAN

| Nama                    | NIM       | Tugas                                                                                                                         |
| ----------------------- | --------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Dzaky Pramadhani        |           | Membuat logika kode eksplorer di main.py                                                                                      |
| Muhammad Rafly          |           | Membuat logika kode menu game di menu.py                                                                                      |
| Reyhan Capri Moraga     | 123140022 | Membuat logika kode battle turn based antar hero dan enemy di battle.py, mengintegrasi kode main.py, battle.py dengan menu.py |
| Muhammad Royhan Alfitra |           | Membuat dan mengumpulkan semua asset game                                                                                     |
| Andini Rahma Kemala     | 123140067 | Membuat dokumentasi game                                                                                                      |

# 🌌 Utopia: Unpromised Land

👾 Game RPG top-down bergaya chibi pixel art yang menyatukan nuansa gelap dan fantasi dalam petualangan penuh misteri!

## 🚀 Cara Menjalankan Game

1. Pastikan Python dan pip terinstall di sistem
2. Install dependencies yang dibutuhkan:

```bash
pip install pygame
```

3. Jalankan game melalui menu.py:

```bash
python menu.py
```

## 🎮 Struktur Kode

```
.
├── menu.py              # Entry point untuk memulai game
├── battle.py            # Sistem battle dengan bosses
├── handler.py           # Penghubung antara menu dan battle
├── main.py             # Game world dan explorasi
├── sprites.py          # Base class untuk semua sprite game
├── player.py           # Implementasi karakter player
├── boss.py             # Base class untuk semua bosses
├── config.py           # Konfigurasi game dan constants
├── game_data.py        # Shared data dan utilities
├── display_manager.py  # Scaling dan display handling
└── characters/         # Implementasi karakter spesifik
    ├── ashenknight.py
    ├── bloodreaper.py
    ├── cyclops.py
    ├── deathsentry.py
    └── ...
```

## 🎨 Fitur Game

### 🦸‍♂️ Karakter Pilihan

- **Ashen Knight**: Tank warrior dengan kemampuan shield
- **Blood Reaper**: DPS assassin dengan lifesteal

### ⚔️ Sistem Battle

- Turn-based battle system
- Multiple boss encounters
- Combo system
- Skill & ultimate abilities
- Energy management

### 🌍 Explorasi

- Top-down world exploration
- Enemy encounters
- Collision system
- Camera tracking

### 🎯 RPG Elements

- Stat progression system
- Leveling & upgrades
- Multiple boss types
- Character abilities

## 🛠️ Komponen Teknis

### Scaling System

- Adaptive resolution scaling
- UI/Asset scaling
- Cross-resolution compatibility

### State Management

- Menu state
- Battle state
- Exploration state
- Loading transitions

### Sound System

- BGM untuk menu, battle dan explorasi
- SFX untuk actions dan abilities
- Volume control

## 🎮 Controls

### Menu

- Arrow Keys: Navigasi menu
- Enter: Select
- Q: Quit

### Battle

- A: Basic Attack
- S: Skill (Ashen Knight)
- D: Ultimate (Ashen Knight)
- F: Heal
- Q: Exit battle

### Exploration

- Arrow Keys / WASD: Movement
- Interact with enemies to trigger battles

## 🔧 Development

### Prerequisites

- Python 3.x
- Pygame library
- JSON untuk save data

### Asset Credits

- Pixel art assets dibuat in-house
- Sound assets dari royalty-free sources

## 📝 Notes

- Save data disimpan di tree_stats.json
- Battle state ditrack melalui alive_status.json
- Settings dapat diubah melalui menu options

---

Made with 💻 by SmollJesteR for tugas OOP
