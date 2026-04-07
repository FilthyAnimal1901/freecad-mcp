# LUCKY BANDIT v4.3 — Windows Setup Guide

Complete walkthrough to generate the STEP file and upload it to Onshape from a Windows PC.

---

## Step 1: Install Python

1. Download **Python 3.11** from https://www.python.org/downloads/release/python-3119/
   - Scroll down and grab **Windows installer (64-bit)**
2. Run the installer
   - **CHECK the box** "Add python.exe to PATH" at the bottom of the first screen
   - Click "Install Now"
3. Verify — open **Command Prompt** (Win+R, type `cmd`, Enter):
   ```cmd
   python --version
   ```
   You should see `Python 3.11.x`.

> **Why 3.11?** CadQuery requires Python 3.9–3.12. It does not yet work with Python 3.13+.

---

## Step 2: Install Git (if not already installed)

If `git --version` doesn't work in Command Prompt:

1. Download from https://git-scm.com/download/win
2. Run the installer with default settings
3. Restart Command Prompt, then verify: `git --version`

---

## Step 3: Clone the Repo

```cmd
cd %USERPROFILE%\Desktop
git clone https://github.com/FilthyAnimal1901/freecad-mcp.git
cd freecad-mcp
git checkout claude/cadquery-bandit-vessel-H58kx
```

---

## Step 4: Install Python Dependencies

```cmd
pip install cadquery requests
```

This installs:
- **cadquery** — the CAD modeling library (builds the 3D geometry)
- **requests** — HTTP library (used by the Onshape uploader)

If you get an error about `cadquery`, try:
```cmd
pip install cadquery==2.4.0
```

---

## Step 5: Generate the STEP File

```cmd
cd examples\cadquery
python lucky_bandit_v43.py
```

You should see:
```
STEP file exported -> ...\lucky_bandit_v43.step
```

The `.step` file is now sitting in `examples\cadquery\`.

---

## Step 6: Upload to Onshape

You have two options:

### Option A: Automatic Upload (via script)

**6A-1. Get Onshape API Keys:**
1. Log into https://cad.onshape.com
2. Click your **profile icon** (top-right corner) -> **My account**
3. Go to the **API keys** tab
   - Or go directly to: https://dev-portal.onshape.com/keys
4. Click **Create new API key**
5. Grant **Read and Write** permissions on Documents
6. Copy both the **Access Key** and **Secret Key**
   - The secret key is only shown ONCE — save it somewhere safe

**6A-2. Create a `.env` file:**

In the `examples\cadquery\` folder, create a new file called `.env` (no filename, just the extension). In Notepad:
- File -> Save As
- Change "Save as type" to **All Files**
- Filename: `.env`
- Paste this content:

```
ONSHAPE_ACCESS_KEY=paste_your_access_key_here
ONSHAPE_SECRET_KEY=paste_your_secret_key_here
```

**6A-3. Run the upload:**

```cmd
python upload_to_onshape.py
```

Output:
```
STEP file : ...\lucky_bandit_v43.step  (XXX KB)
Creating Onshape document: 'LUCKY BANDIT v4.3 - Pressure Vessel' ...
  Document ID : abc123...
  Workspace ID: def456...
Uploading STEP file ...
  Upload complete!

Open in Onshape:
  https://cad.onshape.com/documents/abc123.../w/def456...
```

Click that link to open your model.

---

### Option B: Manual Upload (no API keys needed)

1. Open https://cad.onshape.com and log in
2. Click **Create** -> **Document...**
3. Name it `LUCKY BANDIT v4.3`
4. Inside the document, click the **+** button on the tab bar at the bottom
5. Select **Import**
6. Browse to `Desktop\freecad-mcp\examples\cadquery\lucky_bandit_v43.step`
7. Click **Open** — Onshape will import and translate the solid

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python` not recognized | Re-run the Python installer and check "Add to PATH", or use `py` instead of `python` |
| `pip install cadquery` fails with build errors | Make sure you're on Python 3.11 (not 3.13). Try: `pip install cadquery==2.4.0` |
| `ModuleNotFoundError: No module named 'cadquery'` | Run `pip install cadquery` again, or check you're using the right Python: `where python` |
| Upload script says "403 Forbidden" | Your API keys may not have write permissions. Regenerate them with Read+Write on Documents |
| STEP file is 0 KB | The CadQuery script hit an error. Run it again and check for error messages |
