"""
Download and convert datasets to standardized format.

Example usage:
    python scripts/process_dataset.py
"""

import argparse
from pathlib import Path
from datasets import load_dataset
from PIL import Image
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.images import convert_to_pil_image
from utils.validator import validate_task_data


def download_videothinkbench(output_dir: Path, split: str = "test", limit: int = None):
    """Download VideoThinkBench from HuggingFace and convert to standard format."""
    
    print(f"Downloading VideoThinkBench (split: {split})...")
    
    # Load dataset from HuggingFace
    dataset = load_dataset(
        "video-think-bench/VideoThinkBench",
        split=split,
    )
    
    if limit:
        dataset = dataset.select(range(min(limit, len(dataset))))
    
    print(f"Processing {len(dataset)} samples...")
    
    # Process each sample
    successful = 0
    for idx, item in enumerate(dataset):
        if process_sample(item, idx, split, output_dir):
            successful += 1
            if (idx + 1) % 10 == 0:
                print(f"Processed {idx + 1}/{len(dataset)}")
    
    print(f"\n✓ Successfully converted {successful}/{len(dataset)} samples")
    return successful


def process_sample(item: dict, idx: int, split: str, output_dir: Path) -> bool:
    """Process a single sample and save to disk."""
    
    # Extract first frame
    first_frame = convert_to_pil_image(item.get("image"))
    if not first_frame:
        print(f"Warning: Invalid first frame at index {idx}")
        return False
    
    # Extract prompt
    prompt = item.get("question") or item.get("prompt") or "Solve this visual reasoning task."
    prompt = str(prompt).strip()
    
    # Extract final frame (required)
    final_frame = convert_to_pil_image(item.get("target_image"))
    if not final_frame:
        print(f"Warning: Invalid final frame at index {idx}")
        return False
    
    # Validate data matches standardized format
    if not validate_task_data(first_frame, prompt, final_frame):
        print(f"Warning: Data validation failed at index {idx}")
        return False
    
    # Create task directory
    domain = item.get("task_type") or item.get("category") or "videothinkbench"
    task_id = f"vtb_{split}_{idx:05d}"
    task_dir = output_dir / f"{domain}_task" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # Write files
    first_frame.save(task_dir / "first_frame.png")
    final_frame.save(task_dir / "final_frame.png")
    (task_dir / "prompt.txt").write_text(prompt)
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Download datasets and convert to standardized format")
    parser.add_argument("--dataset", type=str, default="videothinkbench", help="Dataset name")
    parser.add_argument("--split", type=str, default="test", help="Dataset split")
    parser.add_argument("--output", type=Path, default=Path("data/questions"), help="Output directory")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of samples")
    
    args = parser.parse_args()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Download based on dataset name
    if args.dataset.lower() == "videothinkbench":
        download_videothinkbench(args.output, args.split, args.limit)
    else:
        print(f"Error: Unknown dataset '{args.dataset}'")
        print("Available datasets: videothinkbench")


if __name__ == "__main__":
    main()

