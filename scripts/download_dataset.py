"""
Download and convert datasets to VMEvalKit format.

Example usage:
    python scripts/download_dataset.py --dataset videothinkbench --limit 10
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
    
    # Extract goal (image or text)
    final_frame = convert_to_pil_image(item.get("target_image"))
    goal_text = item.get("answer") or item.get("target_text")
    
    # Create metadata
    domain = item.get("task_type") or item.get("category") or "videothinkbench"
    task_id = f"vtb_{split}_{idx:05d}"
    
    metadata = {
        "domain": domain,
        "task_id": task_id,
        "difficulty": item.get("difficulty"),
        "source": "video-think-bench/VideoThinkBench",
        "split": split,
        "extra": {
            k: v for k, v in item.items()
            if k not in ["image", "target_image", "question", "answer", "prompt"]
            and not isinstance(v, (Image.Image, bytes))
        }
    }
    
    # Validate data matches VMEvalKit format
    if not validate_task_data(first_frame, prompt, final_frame, goal_text, metadata):
        print(f"Warning: Data validation failed at index {idx}")
        return False
    
    # Create task directory
    task_dir = output_dir / f"{domain}_task" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    # Write files
    first_frame.save(task_dir / "first_frame.png")
    
    if final_frame:
        final_frame.save(task_dir / "final_frame.png")
    elif goal_text:
        (task_dir / "goal.txt").write_text(str(goal_text).strip())
    
    (task_dir / "prompt.txt").write_text(prompt)
    (task_dir / "question_metadata.json").write_text(json.dumps(metadata, indent=2))
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Download datasets and convert to VMEvalKit format")
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

