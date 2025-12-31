# Template Data Pipeline

Download datasets from HuggingFace and convert to standardized format.

## Usage

```bash
# Install
pip install -r requirements.txt

# Get dataset → outputs to data/questions/
python scripts/process_dataset.py

# Upload to S3
python utils/upload_to_s3.py --action upload --input data/questions --bucket BUCKET
```

## Output Format

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png
├── final_frame.png
├── prompt.txt
└── ground_truth.mp4 (optional)
```

## AWS Setup

```bash
export AWS_ACCESS_KEY_ID="key"
export AWS_SECRET_ACCESS_KEY="secret"
export AWS_DEFAULT_REGION="us-east-1"
```

## Dependencies

- `numpy==1.26.4`
- `Pillow==10.3.0`
- `datasets==2.19.0`
- `huggingface-hub==0.23.0`
- `boto3==1.34.110`
