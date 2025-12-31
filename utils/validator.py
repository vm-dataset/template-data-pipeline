"""
Validator utilities for checking data consistency with standardized format.

Standardized format:
    data/questions/{domain}_task/{task_id}/
    ├── first_frame.png          (required)
    ├── final_frame.png          (required)
    ├── prompt.txt               (required)
    └── ground_truth.avi         (optional)

Functions:
- validate_task_data() - Validate data matches standardized format
- validate_task_directory() - Validate directory structure
"""

from pathlib import Path
from typing import Dict, Any
from PIL import Image


def validate_task_data(
    first_frame: Image.Image,
    prompt: str,
    final_frame: Image.Image,
    metadata: Dict[str, Any] = None,
) -> bool:
    """Validate task data matches standardized format.
    
    Args:
        first_frame: Initial state image (required)
        prompt: Natural language instruction (required)
        final_frame: Final state image (required)
        metadata: Task metadata dict (required)
        
    Returns:
        True if valid, False otherwise
    """
    # Check required fields
    if first_frame is None:
        return False
    
    if not prompt or not prompt.strip():
        return False
    
    # final_frame is now required
    if final_frame is None:
        return False
    
    # Check metadata has required fields
    if not metadata:
        return False
    
    required_metadata_fields = ["domain", "task_id", "source"]
    for field in required_metadata_fields:
        if field not in metadata:
            return False
    
    return True


def validate_task_directory(task_dir: Path) -> bool:
    """Validate task directory structure matches standardized format.
    
    Args:
        task_dir: Path to task directory
        
    Returns:
        True if valid, False otherwise
    """
    if not task_dir.exists() or not task_dir.is_dir():
        return False
    
    # Check required files
    first_frame = task_dir / "first_frame.png"
    final_frame = task_dir / "final_frame.png"
    prompt_file = task_dir / "prompt.txt"
    
    if not first_frame.exists():
        return False
    
    if not final_frame.exists():
        return False
    
    if not prompt_file.exists():
        return False
    
    return True

