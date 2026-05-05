# Osmosis — Installation Guide

Osmosis is a Pythonic wrapper around the OpenStudio SDK. This guide walks through cloning the repo, installing it as an editable package, and configuring VS Code so Pylance can resolve imports.

---

## Prerequisites

- Python 3.10 or later installed and on your PATH
- `pip` available (`python -m pip --version` should work)
- [VS Code](https://code.visualstudio.com/) with the [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) extension
- The [OpenStudio SDK](https://github.com/NREL/OpenStudio/releases) Python bindings installed in your environment

---

## 1. Clone the Repository

```bash
git clone https://github.com/SMarentette/Osmosis.git
cd Osmosis
```

---

## 2. Install Osmosis into Your Python Environment

Installing as **editable** (`-e`) means any changes to the source are picked up immediately — no reinstall required.

### Option A — Into your global/user Python (recommended for use across projects)

```bash
python -m pip install --user -e "C:\path\to\Osmosis"
```

Replace `C:\path\to\Osmosis` with wherever you cloned the repo.

### Option B — Into a virtual environment

```bash
# Create and activate a venv inside the project (or wherever you prefer)
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -e .
```

---

## 3. Verify the Installation

Open a Python shell and confirm the import works:

```python
import osmosis as osmo
print(osmo.__file__)
```

You should see a path pointing back to the cloned repo's `osmosis/` folder.

---

## 4. Configure VS Code / Pylance

Pylance needs to know where to find the `osmosis` package, especially when it is installed with `--user` or into a venv that VS Code hasn't selected.

### 4a. Select the Correct Python Interpreter

1. Open the Command Palette (`Ctrl+Shift+P`)
2. Run **Python: Select Interpreter**
3. Choose the interpreter that matches the environment you installed Osmosis into

### 4b. Add the Source Root to `extraPaths`

Open your workspace or user `settings.json` (`Ctrl+Shift+P` → **Preferences: Open Workspace Settings (JSON)**) and add:

```json
{
    "python.analysis.extraPaths": [
        "C:/path/to/Osmosis"
    ]
}
```

Replace `C:/path/to/Osmosis` with the absolute path to the cloned repo root (the folder that contains the `osmosis/` package directory). Use forward slashes or escaped backslashes.

> **Tip:** If you're working inside the Osmosis repo itself, you can use a relative path:
> ```json
> {
>     "python.analysis.extraPaths": ["."]
> }
> ```

### 4c. Reload the Window

After saving `settings.json`, reload VS Code so Pylance picks up the change:

- `Ctrl+Shift+P` → **Developer: Reload Window**

Pylance should now resolve `import osmosis` without squiggles.

---

## 5. Running the Tests

From the repo root with your environment active:

```bash
pytest
```

All tests live in the `tests/` folder. A passing run confirms your installation is working correctly.
