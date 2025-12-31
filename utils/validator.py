"""
Validator utilities for checking data consistency with VMEvalKit format.

VMEvalKit format:
    data/questions/{domain}_task/{task_id}/
    ├── first_frame.png          (required)
    ├── final_frame.png or goal.txt (one required)
    ├── prompt.txt               (required)
    └── question_metadata.json   (required)

Functions:
- validate_task_data() - Validate data matches VMEvalKit format
- validate_task_directory() - Validate directory structure
"""

from pathlib import Path
from typing import Dict, Any
from PIL import Image


def validate_task_data(
    first_frame: Image.Image,
    prompt: str,
    final_frame: Image.Image = None,
    goal_text: str = None,
    metadata: Dict[str, Any] = None,
) -> bool:
    """Validate task data matches VMEvalKit format.
    
    Args:
        first_frame: Initial state image (required)
        prompt: Natural language instruction (required)
        final_frame: Goal state image (optional if goal_text provided)
        goal_text: Goal state text (optional if final_frame provided)
        metadata: Task metadata dict (required)
        
    Returns:
        True if valid, False otherwise
    """
    # Check required fields
    if first_frame is None:
        return False
    
    if not prompt or not prompt.strip():
        return False
    
    # Must have either final_frame OR goal_text
    if final_frame is None and not goal_text:
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
    """Validate task directory structure matches VMEvalKit format.
    
    Args:
        task_dir: Path to task directory
        
    Returns:
        True if valid, False otherwise
    """
    if not task_dir.exists() or not task_dir.is_dir():
        return False
    
    # Check required files
    first_frame = task_dir / "first_frame.png"
    prompt_file = task_dir / "prompt.txt"
    metadata_file = task_dir / "question_metadata.json"
    
    if not first_frame.exists():
        return False
    
    if not prompt_file.exists():
        return False
    
    if not metadata_file.exists():
        return False
    
    # Check for goal (either final_frame.png or goal.txt)
    final_frame = task_dir / "final_frame.png"
    goal_txt = task_dir / "goal.txt"
    
    if not final_frame.exists() and not goal_txt.exists():
        return False
    
    return True

