# Bangladesh Inland Vessel Statutory Compliance & Scantlings Suite

Professional Naval Architecture & Marine Structural Engineering Suite conforming to the **Bangladesh Inland Shipping Rules 2001 (SRO 308/Law-2001)** and **Inland Shipping Ordinance 1976**.

---

## 🚀 Running as a Native Desktop Application

The application runs as a **Native Windows Desktop Application** using Windows Edge App Mode (`--app=...`).

### Key Benefits:
- **Zero New Dependencies:** Uses Microsoft Edge built into Windows 10 & 11 (0 MB extra download).
- **Native Look & Feel:** Chromeless standalone desktop window — **no browser tabs, no URL bar, no bookmarks, no navigation buttons**.
- **Isolated App Profile:** Dedicated profile in `%LOCALAPPDATA%\BanglaScantlingApp\EdgeProfile` ensures your app settings, zoom, and window sizing stay preserved without affecting personal browser sessions.
- **Automated Lifecycle:** Automatically starts the local backend server, conducts health checks, and shuts down cleanly when the window is closed.

---

## 🖥️ How to Launch

You have four convenient ways to launch the software:

1. **Desktop Shortcut:**
   - Double-click the **"Bangladesh Scantlings Suite"** shortcut on your Windows Desktop (with custom app icon).
2. **Windowless Launcher (Silent):**
   - Double-click `BanglaScantling.vbs` (launches directly with **no black command prompt** window).
3. **Batch Launcher:**
   - Double-click `BanglaScantling.bat` or `start_app.bat`.
4. **Command Line:**
   ```bash
   python run_app.py
   ```

---

## 🛠️ Recreating Desktop Shortcut

If you ever need to restore or recreate the desktop shortcut, run:
```bash
python create_desktop_shortcut.py
```

---

## 🚢 Core Modules
1. **Dashboard & Vessel Particulars:** Principle dimensions ($L_{BP}$, $B$, $D$, $d$, $C_b$, speed, route multiplier $k_t$).
2. **Scantling Calculation & Schedule Tables:** Rules 8–31 and statutory Schedule Tables 1–67.
3. **Hull Longitudinal Strength (Rules 209 & 223):** Midship section modulus integration, interactive strake selector, Table 66 & 67 stress evaluation.
4. **Lightship Weight & Longitudinal Centers:** Structural weight summation, live Excel formulas, and standard statutory outfitting allowances (56%).
5. **Statutory PDF Deliverables:** 4-Page Hull Strength Booklet, Detail Calculation Booklet, and Lightship Booklet with Supervisor review blocks and seals on every page.
