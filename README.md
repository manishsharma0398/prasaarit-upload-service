# prasaarit-upload-service

FastAPI-based upload service for Prasaarit. Handles presigned S3 URL generation for both single-file and multipart uploads, deployed on AWS Lambda via Mangum.

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) — install with:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

---

## Getting started after cloning

Run these steps once after cloning the repo on a new machine:

```bash
# 1. Install all dependencies (production + dev + lint groups)
uv sync --all-groups

# 2. Install pre-commit hooks into git
uv run pre-commit install

# 3. (Optional) Apply formatting to all existing files
uv run pre-commit run --all-files
git add .
git commit -m "chore: apply formatting"
```

After step 2, hooks run automatically on every `git commit` — no further setup needed.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AWS_REGION` | `ap-south-1` | AWS region for S3 |
| `RAW_BUCKET_NAME` | `prasaarit-stg-raw-uploads` | S3 bucket for raw uploads |


---

## Running locally

```bash
uv run fastapi dev src/main.py
```

---

## API Endpoints

### `POST /generate-presigned-url?type=single|multipart`

Generates a presigned S3 URL for uploading a file directly to S3.

**Query params**

| Param | Values | Default | Description |
|-------|--------|---------|-------------|
| `type` | `single`, `multipart` | `single` | Upload mode |

**Request body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contentType` | string | ✅ | MIME type (`video/mp4`, `video/webm`, etc.) |
| `fileSize` | number | ✅ | File size in bytes (max 5 GB) |
| `s3Key` | string | multipart only | S3 key returned from `/initiate-multipart-upload` |
| `uploadId` | string | multipart only | Upload ID from `/initiate-multipart-upload` |
| `partNumber` | integer (1–10000) | multipart only | Chunk part number |

---

### `POST /initiate-multipart-upload`

Starts a multipart upload session. Returns `uploadId` and `s3Key` to use for all subsequent part and complete calls.

---

### `POST /complete-multipart-upload`

Finalises a multipart upload. S3 assembles all parts into the final object.

**Request body**

| Field | Type | Description |
|-------|------|-------------|
| `uploadId` | string | From `/initiate-multipart-upload` |
| `s3Key` | string | From `/initiate-multipart-upload` |
| `parts` | `[{ PartNumber, ETag }]` | Collected from each S3 `PUT` response header |

---

### `POST /abort-multipart-upload`

Cancels an in-progress multipart upload and cleans up all uploaded parts from S3.

---

## Upload flows

### Single upload

```
1. POST /generate-presigned-url?type=single
   { contentType, fileSize }
   → { presignedUrl, mediaId, expiresIn }

2. PUT <presignedUrl>
   Headers: { Content-Type: <contentType> }
   Body: <file bytes>
```

> The `Content-Type` header is **required** on the PUT — it is part of the AWS signature and S3 will reject the request with a `403` if omitted.

### Multipart upload

```
1. POST /initiate-multipart-upload
   { contentType, fileSize }
   → { uploadId, s3Key }

2. For each chunk:
   POST /generate-presigned-url?type=multipart
   { contentType, fileSize, s3Key, uploadId, partNumber }
   → { presignedUrl, mediaId, expiresIn }

   PUT <presignedUrl>
   Body: <chunk bytes>
   ← ETag header (save this per part)

3. POST /complete-multipart-upload
   { uploadId, s3Key, parts: [{ PartNumber, ETag }] }
   → { success: true, uploadId }
```

> Part numbers must be sequential starting from 1. ETags come directly from S3 in the `PUT` response header — they are never returned by this service.

---

## Dependency groups

This project uses [uv dependency groups](https://docs.astral.sh/uv/concepts/dependencies/#dependency-groups) to separate concerns.

| Group | Purpose | Install command |
|-------|---------|-----------------|
| *(default)* | Production dependencies | `uv sync` |
| `dev` | boto3, type stubs, pre-commit | `uv sync --group dev` |
| `lint` | black, isort, flake8, bandit | `uv sync --group lint` |

### Common commands

```bash
# Install all groups
uv sync --all-groups

# Install a specific group only
uv sync --group lint

# Add a package to a group
uv add --group lint <package>

# Run a tool from a group without activating the venv
uv run --group lint flake8 src/
```

---

## Linting

Run individual tools directly:

```bash
uv run --group lint flake8 src/
uv run --group lint black src/
uv run --group lint isort src/
uv run --group lint bandit -r src/
```

---

## Pre-commit

Hooks run automatically on `git commit`. To set up after cloning:

```bash
uv run pre-commit install
```

### Run on all files

Useful when adding pre-commit to an existing repo, adding a new hook, or
reformatting everything at once:

```bash
uv run pre-commit run --all-files
```

Hooks that auto-fix files (black, isort, end-of-file-fixer) will report
`Failed` on the first pass because they modified files. Stage the changes
and run again — everything will pass on the second run.

```bash
uv run pre-commit run --all-files  # hooks fix files
git add .
uv run pre-commit run --all-files  # all pass
git commit -m "chore: apply formatting"
```

### Run a specific hook only

```bash
uv run pre-commit run black --all-files
uv run pre-commit run flake8 --all-files
```
