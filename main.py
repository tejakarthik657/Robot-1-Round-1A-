import os
import argparse
import yaml
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

from utils.pdf_utils import PDFOutlineExtractor
from utils.export_utils import save_outline

def setup_logging(log_dir):
    """Sets up a rotating log file for the application."""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "extraction.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def process_pdf(pdf_path, config, output_formats):
    """
    Processes a single PDF file: extracts outline and saves it.
    Returns the status and filename.
    """
    filename = os.path.basename(pdf_path)
    try:
        extractor = PDFOutlineExtractor(pdf_path, config)
        outline = extractor.extract()

        for fmt in output_formats:
            output_filename = os.path.splitext(filename)[0] + f".{fmt}"
            output_path = os.path.join(config['output_dir'], output_filename)
            save_outline(outline, output_path, fmt)

        return (f"✅ Success: {filename}", True)
    except Exception as e:
        logging.error(f"Failed to process {filename}: {e}", exc_info=True)
        return (f"❌ Failed: {filename} ({type(e).__name__})", False)

def main():
    parser = argparse.ArgumentParser(description="Extract a structured outline from PDF files.")
    parser.add_argument("--config", default="config.yaml", help="Path to the configuration file.")
    parser.add_argument("--format", choices=['json', 'md', 'all'], default='json', help="Output format(s).")
    parser.add_argument("--workers", type=int, default=os.cpu_count(), help="Number of parallel processes to use.")
    args = parser.parse_args()

    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    setup_logging(config['log_dir'])

    input_dir = config['input_dir']
    if not os.path.isdir(input_dir):
        logging.error(f"Input directory not found: {input_dir}")
        return

    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    if not pdf_files:
        logging.warning("No PDF files found in the input directory.")
        return

    output_formats = ['json', 'md'] if args.format == 'all' else [args.format]
    
    logging.info(f"Starting processing of {len(pdf_files)} PDF(s) with {args.workers} worker(s)...")
    logging.info(f"Output format(s): {', '.join(output_formats)}")
    
    success_count = 0
    fail_count = 0
    
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_pdf, path, config, output_formats): path for path in pdf_files}
        
        # Use tqdm for a progress bar
        progress_bar = tqdm(as_completed(futures), total=len(pdf_files), desc="Processing PDFs")
        for future in progress_bar:
            message, success = future.result()
            if success:
                success_count += 1
            else:
                fail_count += 1
            logging.info(message)
    
    logging.info("=" * 30)
    logging.info("Processing complete.")
    logging.info(f"Successfully processed: {success_count}")
    logging.info(f"Failed to process: {fail_count}")
    logging.info(f"Outputs saved in '{config['output_dir']}' directory.")
    logging.info(f"Detailed logs available in '{config['log_dir']}/extraction.log'")

if __name__ == "__main__":
    main()