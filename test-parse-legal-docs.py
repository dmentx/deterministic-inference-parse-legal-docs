# Requires PyTorch 2.9.0 or higher as well as https://github.com/vllm-project/vllm/pull/24583 and https://github.com/iamarunbrahma/vision-parse/pull/49


import os
import traceback
from pathlib import Path
from datetime import datetime
from tqdm.notebook import tqdm  
from tqdm import tqdm           
import difflib


from prompts.parse_prompts import ZERO_SHOT, ZERO_SHOT_V2, FEW_SHOT


try:
    from vision_parse import VisionParser
    from vision_parse.llm import LLMError
except ImportError:
    print("Could not import VisionParser/LLMError. Fallback in use.")

    class LLMError(Exception):
        pass

    class VisionParser:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("VisionParser not available")


custom_prompt = ZERO_SHOT


openai_cfg = {
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", "EMPTY"),
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1"),
    "api_key": os.getenv("OPENAI_API_KEY", "EMPTY"),
    "base_url": os.getenv("OPENAI_BASE_URL", "http://localhost:8000/v1"),
}
os.environ.setdefault("OPENAI_API_KEY", "EMPTY")
os.environ.setdefault("OPENAI_BASE_URL", "http://localhost:8000/v1")

MISTRAL_MODEL_ID = "unsloth/Mistral-Small-3.1-24B-Instruct-2503-bnb-4bit"


try:
    parser = VisionParser(
        model_name=MISTRAL_MODEL_ID,
        openai_config=openai_cfg,
        image_mode=None,
        detailed_extraction=True,
        enable_concurrency=False,
        custom_prompt=custom_prompt,
        temperature=0.0,
        top_p=1.0,
        frequency_penalty=0.0,
    )
except Exception as init_err:
    print(f"🚨 Failed to initialize VisionParser: {init_err}")
    exit()

pdf_directory = Path("./pdfs/")
output_directory = Path("./outputMD")
output_directory.mkdir(parents=True, exist_ok=True)

pdf_files = list(pdf_directory.glob("*.pdf")) + list(pdf_directory.glob("*.PDF"))
if not pdf_files:
    print(f"No PDF files found in {pdf_directory}. Exiting.")
    exit()

print(f"Found {len(pdf_files)} PDF files in {pdf_directory}. Starting conversion…")


failed_files = []
content_filter_files = []
error_log_path = Path("error_log.txt")

NUM_RUNS = 20  


main_pbar = tqdm(pdf_files, desc="Converting PDFs", unit="file", leave=True)

for pdf_path in main_pbar:
    pdf_filename = pdf_path.name
    main_pbar.set_description(f"Processing {pdf_filename[:25]}...")

    try:
        run_results = []

        for run_idx in range(NUM_RUNS):
            markdown_pages = parser.convert_pdf(str(pdf_path))
            markdown_content = "\n".join(
                page.strip() for page in markdown_pages if page and not page.isspace()
            ).strip()
            run_results.append(markdown_content)

            out_file = output_directory / f"{pdf_path.stem}_run{run_idx+1}.md"
            out_file.write_text(markdown_content, encoding="utf-8")

        e
        unique_results = set(run_results)
        print(f"\n📄 {pdf_filename}: {NUM_RUNS} Runs, {len(unique_results)} unique results")


    except LLMError as e:
        error_msg = str(e)
        tqdm.write(f"LLM Error processing {pdf_filename}: {e}")
        failed_files.append((pdf_filename, f"LLM Error: {e}"))
        log_entry = f"[{datetime.now().isoformat()}] {pdf_filename}: LLM ERROR - {e}\n"
        try:
            with open(error_log_path, "a", encoding="utf-8") as log:
                log.write(log_entry)
                log.write("-" * 40 + "\n")
        except Exception as log_e:
            tqdm.write(f"Failed to write to error log '{error_log_path}': {log_e}")

    except Exception as e:
        tqdm.write(f"Error processing {pdf_filename}: {type(e).__name__} - {e}")
        failed_files.append((pdf_filename, f"Unexpected Error: {type(e).__name__} - {e}"))
        tb_str = traceback.format_exc()
        try:
            with open(error_log_path, "a", encoding="utf-8") as log:
                log.write(f"[{datetime.now().isoformat()}] {pdf_filename}: UNEXPECTED ERROR\n")
                log.write(f"Error Type: {type(e).__name__}\n")
                log.write(f"Error Message: {e}\n")
                log.write("Traceback:\n")
                log.write(tb_str)
                log.write("-" * 40 + "\n")
        except Exception as log_e:
            tqdm.write(f"Failed to write to error log '{error_log_path}': {log_e}")

main_pbar.close()


print("\n" + "=" * 50)
print("Finished processing all PDF files.")
print("=" * 50)

total_processed = len(pdf_files)
total_failed = len(failed_files)
total_succeeded = total_processed - total_failed

print(f"Processed: {total_processed}")
print(f"Succeeded: {total_succeeded}")
print(f"Failed:    {total_failed}")

if failed_files:
    print("-" * 50)
    print(f"\n{total_failed} files could not be processed:")
    other_failures = [f for f in failed_files if f[0] not in content_filter_files]
    if other_failures:
        print(f"\n Due to other errors ({len(other_failures)}):")
        for name, reason in other_failures:
            reason_short = (reason[:70] + "...") if len(reason) > 70 else reason
            print(f"    • {name} - Reason: {reason_short}")

    print(f"\nDetails about errors can be found in '{error_log_path}' (if logging was successful).")
else:
    print("\nAll PDFs were processed successfully!")

print("=" * 50)
