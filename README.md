# doppler-colab

Seamlessly and securely inject Doppler secrets into Google Colab interactive environments.

When working in ephemeral environments like Google Colab, managing secrets securely is a challenge. `doppler-colab` natively integrates with Colab's built-in Secrets management to securely fetch your environment variables from the Doppler API and inject them silently into `os.environ`.

No CLI dependencies, no leaking print statements, and downstream libraries instantly work.

## Installation

Install the package directly inside your Colab notebook:

```python
!pip install -q doppler-colab
```

## Setup

1. Generate a **Service Token** inside your Doppler dashboard. (Service tokens enforce scoping and ensure you safely access the correct environment).
2. Open your Google Colab notebook.
3. Click the 🔑 **Secrets** icon on the left sidebar.
4. Add a new secret with the name `DOPPLER_TOKEN` and paste in your Service Token (`dp.st...`).
5. Ensure the **"Notebook access"** toggle is explicitly switched **ON** next to the token, enabling read-access for your environment.

*(Fallback: If you are not in Colab, the package will automatically check `os.environ["DOPPLER_TOKEN"]` as a fallback).*

## Usage

### Method 1: Python API

Invoke the package manually to fetch and load your secrets:

```python
import doppler_colab
doppler_colab.load()

# ✅ Successfully injected 14 secrets from Doppler [Project: your-project] into the environment.
```

### Method 2: IPython Cell Magic

For a cleaner interactive workflow, use the `%doppler_load` magic command at the top of your cells:

```python
import doppler_colab
%doppler_load
```

## Secure by Default

- **Silent Payloads**: `doppler-colab` will never print the returned payload or tokens. You only receive a safe confirmation of the number of imported parameters.
- **Write Warnings**: If your Service Token contains unrestricted write capabilities, the package will proactively warn you to utilize a Read-Only token for security.

## Disclaimer & Acknowledgements

*Please note: This is a community-driven project and is **not** an official Doppler product, nor is it officially supported by Doppler (though we'd be happy to change that!).*

This refactoring and adaptation to Google Colab would not have been possible without the foundational work of the original authors at Doppler on the `python-doppler-env` package. 

For bug reports or feature requests specifically related to this Colab adaptation, please create an issue on this repository.
