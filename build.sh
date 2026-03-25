#!/bin/bash

set -e

PACKAGE_NAME="prasaarit_upload_service"
BUILD_DIR=".build"
ZIP_FILE="${PACKAGE_NAME}.zip"

echo "🧹 Cleaning previous build..."
rm -rf "$BUILD_DIR"
rm -f "$ZIP_FILE"

echo "📦 Installing runtime dependencies..."
mkdir -p "$BUILD_DIR"
uv export --no-dev --no-hashes -o "$BUILD_DIR/requirements.txt"
uv pip install \
  --target "$BUILD_DIR" \
  -r "$BUILD_DIR/requirements.txt"

echo "📁 Copying source code..."
cp -r src "$BUILD_DIR/src"

echo "🗜️  Zipping..."
cd "$BUILD_DIR"
zip -r "../$ZIP_FILE" . -x "*.pyc" -x "*/__pycache__/*" -x "*.dist-info/*" -x "requirements.txt"
cd ..

echo "✅ Done! Created: $ZIP_FILE"
echo "📊 Size: $(du -sh $ZIP_FILE | cut -f1)"