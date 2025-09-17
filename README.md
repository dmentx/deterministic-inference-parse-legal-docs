# deterministic-inference-parse-legal-docs

 Utilities for running deterministic, prompt-driven parsing of legal PDF documents into Markdown using the `VisionParser` pipeline and custom prompt presets.

  ## Features
  - Runs `VisionParser.convert_pdf` repeatedly (default: 20 passes) to compare deterministic outputs.
  - Ships with zero-shot and few-shot prompt templates tailored for legal clause hierarchy and table preservation (`prompts/parse_prompts.py`).
  - Persists each Markdown run to `outputMD/`.

  ## Requirements
  - Python 3.8+
  - PyTorch 2.9.0+ plus Triton (see `pyproject.toml` dependencies).
  - `vision_parse` with deterministic inference support (https://github.com/iamarunbrahma/vision-parse/pull/49).
  - vLLM with the deterministic-inference patch (https://github.com/vllm-project/vllm/pull/24583).
  - Access to the UnsloTH `Mistral-Small-3.1-24B-Instruct-2503-bnb-4bit` model (default) or a compatible alternative.
  - Environment variables `OPENAI_API_KEY` and `OPENAI_BASE_URL` (defaults fall back to `EMPTY` and `http://localhost:8000/v1`).

  ## Usage
  1. Install dependencies (including patched `vision_parse` and vLLM) into your environment.
  2. Place one or more contract PDFs inside `./pdfs/`.
  3. Run the batch converter:

     ```bash
     python test-parse-legal-docs.py

  4. Review Markdown outputs in ./outputMD/ (one file per run, e.g., contract_run3.md).
  5. Inspect error_log.txt for any LLM or runtime issues.


  ## Project Structure

  - test-parse-legal-docs.py — main batch runner.
  - prompts/ — reusable legal-document prompt definitions.
  - pyproject.toml / uv.lock — dependency metadata.
  - README.md — project overview.
  - LICENSE — MIT license.

  Link to Batch Invariant Ops (https://github.com/thinking-machines-lab/batch_invariant_ops)