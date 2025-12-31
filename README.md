# Template Data Pipeline

**Simple scripts to download benchmark datasets and convert them to standardized format.**

---

## Output Format

All scripts produce this standardized format:

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png          # Initial state image (required)
├── final_frame.png          # Final state image (required)
├── prompt.txt               # Natural language instruction (required)
└── ground_truth.avi         # Ground truth video (optional)
```

---

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/template-data-pipeline.git
cd template-data-pipeline

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### 1. Download Dataset

```bash
# Download VideoThinkBench (test split, first 10 samples)
python scripts/download_dataset.py --dataset videothinkbench --split test --limit 10 --output data/questions

# Download full dataset
python scripts/download_dataset.py --dataset videothinkbench --split test --output data/questions

# Download training split
python scripts/download_dataset.py --dataset videothinkbench --split train --output data/questions
```

### 2. Upload to S3

```bash
# Configure AWS credentials first
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"

# Or use AWS CLI
aws configure

# Upload dataset to S3
python utils/upload_to_s3.py \
  --action upload \
  --input data/questions \
  --bucket your-bucket-name \
  --prefix datasets/videothinkbench/
```

### 3. Download from S3

```bash
# Download dataset from S3
python utils/upload_to_s3.py \
  --action download \
  --bucket your-bucket-name \
  --prefix datasets/videothinkbench/ \
  --output data/questions
```

---

## Scripts

### `scripts/download_dataset.py`

Downloads datasets from HuggingFace and converts to standard format.

**Arguments:**
- `--dataset`: Dataset name (default: `videothinkbench`)
- `--split`: Dataset split (default: `test`)
- `--output`: Output directory (default: `data/questions`)
- `--limit`: Limit number of samples (optional)

**Example:**
```bash
python scripts/download_dataset.py --dataset videothinkbench --limit 10
```

---

## Utilities

### `utils/images.py`

Image utilities for handling various image formats.

**Functions:**
- `convert_to_pil_image(image_input)` - Convert PIL/numpy/paths to PIL Image
- `numpy_to_pil(arr)` - Convert numpy array to PIL Image
- `load_from_path(path)` - Load image from file path

### `utils/validator.py`

Data validator for checking consistency with the standardized format.

**Functions:**
- `validate_task_data(first_frame, prompt, final_frame)` - Validate data structure
- `validate_task_directory(task_dir)` - Validate directory structure

### `utils/upload_to_s3.py`

Universal S3 upload/download utilities.

**Arguments:**
- `--action`: Action to perform (`upload` or `download`)
- `--input`: Input directory (for upload)
- `--output`: Output directory (for download)
- `--bucket`: S3 bucket name (required)
- `--prefix`: S3 prefix/path (optional)

**Upload Example:**
```bash
python utils/upload_to_s3.py \
  --action upload \
  --input data/questions \
  --bucket my-bucket \
  --prefix datasets/
```

**Download Example:**
```bash
python utils/upload_to_s3.py \
  --action download \
  --bucket my-bucket \
  --prefix datasets/ \
  --output data/questions
```

---

## Adding New Datasets

### Step 1: Create Download Function

Edit `scripts/download_dataset.py` and add a new function:

```python
def download_my_dataset(output_dir: Path, split: str = "test", limit: int = None):
    """Download MyDataset from HuggingFace."""
    
    # Load dataset
    dataset = load_dataset("org/dataset-name", split=split)
    
    if limit:
        dataset = dataset.select(range(min(limit, len(dataset))))
    
    # Process each sample
    for idx, item in enumerate(dataset):
        process_my_sample(item, idx, split, output_dir)


def process_my_sample(item: dict, idx: int, split: str, output_dir: Path) -> bool:
    """Process a single sample."""
    
    # Extract images
    first_frame = convert_to_pil_image(item["initial_image"])
    final_frame = convert_to_pil_image(item["target_image"])
    
    # Extract text
    prompt = item["instruction"]
    
    # Create task ID
    task_id = f"my_{split}_{idx:05d}"
    
    # Save to disk
    task_dir = output_dir / f"mydataset_task" / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    
    first_frame.save(task_dir / "first_frame.png")
    final_frame.save(task_dir / "final_frame.png")
    (task_dir / "prompt.txt").write_text(prompt)
    
    return True
```

### Step 2: Register in Main

Add to the `main()` function in `scripts/download_dataset.py`:

```python
if args.dataset.lower() == "mydataset":
    download_my_dataset(args.output, args.split, args.limit)
```

### Step 3: Test

```bash
python scripts/download_dataset.py --dataset mydataset --limit 5
```

---

## Reproducibility Checklist

### Environment Setup

1. **Python Version:**
   ```bash
   python --version  # Should be Python 3.8+
   ```

2. **Install Exact Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Installation:**
   ```bash
   python -c "from PIL import Image; from datasets import load_dataset; print('✓ OK')"
   ```

### Data Download

1. **Set Random Seed (if applicable):**
   ```python
   import random
   import numpy as np
   random.seed(42)
   np.random.seed(42)
   ```

2. **Document Dataset Version:**
   - HuggingFace datasets are versioned automatically
   - Check dataset commit hash: `datasets.get_dataset_config_info()`

3. **Save Download Log:**
   ```bash
   python scripts/download_dataset.py --dataset videothinkbench 2>&1 | tee download.log
   ```

### Validation

1. **Verify Output Structure:**
   ```bash
   # Check directory structure
   find data/questions -type f | head -20
   
   # Count files
   find data/questions -name "first_frame.png" | wc -l
   find data/questions -name "prompt.txt" | wc -l
   find data/questions -name "final_frame.png" | wc -l
   ```

2. **Validate Images:**
   ```python
   from PIL import Image
   from pathlib import Path
   
   for img_path in Path("data/questions").rglob("first_frame.png"):
       img = Image.open(img_path)
       print(f"{img_path}: {img.size} {img.mode}")
   ```

3. **Validate Prompts:**
   ```python
   from pathlib import Path
   
   for prompt_path in Path("data/questions").rglob("prompt.txt"):
       with open(prompt_path) as f:
           prompt = f.read()
           print(f"{prompt_path}: {prompt[:50]}...")
   ```

### S3 Upload

1. **Set AWS Credentials:**
   ```bash
   export AWS_ACCESS_KEY_ID="..."
   export AWS_SECRET_ACCESS_KEY="..."
   export AWS_DEFAULT_REGION="us-east-1"
   ```

2. **Upload with Logging:**
   ```bash
   python utils/upload_to_s3.py \
     --action upload \
     --input data/questions \
     --bucket my-bucket \
     --prefix datasets/videothinkbench/ \
     2>&1 | tee upload.log
   ```

3. **Verify Upload:**
   ```bash
   aws s3 ls s3://my-bucket/datasets/videothinkbench/ --recursive | wc -l
   ```

### Version Control

1. **Document Dataset Version:**
   ```bash
   # Create version file
   echo "videothinkbench" > data/questions/dataset_info.txt
   echo "split: test" >> data/questions/dataset_info.txt
   echo "date: $(date)" >> data/questions/dataset_info.txt
   ```

2. **Save Processing Parameters:**
   ```json
   {
     "dataset": "videothinkbench",
     "split": "test",
     "limit": null,
     "date": "2025-01-01",
     "python_version": "3.10.0",
     "dependencies": "requirements.txt"
   }
   ```

---

## File Structure

```
template-data-pipeline/
├── scripts/
│   └── download_dataset.py      # Dataset-specific processing scripts
├── utils/
│   ├── images.py                # Image utilities
│   ├── validator.py             # Data validator (standardized format)
│   └── upload_to_s3.py          # S3 uploader/downloader
├── data/
│   └── questions/               # Output directory (created)
│       └── {domain}_task/
│           └── {task_id}/
│               ├── first_frame.png
│               ├── final_frame.png
│               ├── prompt.txt
│               └── ground_truth.avi (optional)
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── .gitignore
```

---

## AWS S3 Setup

### Configure AWS CLI

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region name: us-east-1
# Default output format: json
```

### Create S3 Bucket

```bash
# Create bucket
aws s3 mb s3://your-bucket-name --region us-east-1

# Verify bucket exists
aws s3 ls
```

### Set Bucket Permissions (Optional)

```bash
# Make bucket private (recommended)
aws s3api put-bucket-acl --bucket your-bucket-name --acl private

# Enable versioning
aws s3api put-bucket-versioning --bucket your-bucket-name --versioning-configuration Status=Enabled
```

---

## Troubleshooting

### HuggingFace Authentication

Some datasets require authentication:

```bash
# Login to HuggingFace
huggingface-cli login

# Or set token
export HF_TOKEN="your_token"
```

### AWS Credentials

```bash
# Verify credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://your-bucket-name/
```

### Image Conversion Issues

If image conversion fails, check the input format:

```python
from utils.images import convert_to_pil_image

# Debug conversion
image = convert_to_pil_image(your_input)
if image is None:
    print("Conversion failed - check input type")
```

### Data Validation Issues

Check if data matches the standardized format:

```python
from utils.validator import validate_task_data, validate_task_directory

# Validate data structure
is_valid = validate_task_data(first_frame, prompt, final_frame)
if not is_valid:
    print("Data validation failed - missing required fields")

# Validate directory structure
from pathlib import Path
is_valid = validate_task_directory(Path("data/questions/domain_task/task_0001"))
if not is_valid:
    print("Directory structure invalid")
```

---

## Dependencies

All dependencies are pinned to exact versions for reproducibility:

- `numpy==1.26.4` - Array processing
- `Pillow==10.3.0` - Image processing
- `datasets==2.19.0` - HuggingFace datasets
- `huggingface-hub==0.23.0` - HuggingFace API
- `boto3==1.34.110` - AWS S3 client

---

## License

Apache 2.0 - See [LICENSE](LICENSE) file.

---

## Contributing

This is a template repository. To adapt for your needs:

1. Fork the repository
2. Add your dataset download functions to `scripts/download_dataset.py`
3. Update this README with your dataset-specific instructions
4. Maintain the standard output format for compatibility

---

## Related Projects

- **template-data-generator** - Generate synthetic reasoning tasks
