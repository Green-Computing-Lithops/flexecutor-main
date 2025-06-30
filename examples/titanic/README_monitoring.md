# Titanic MinIO Processing Monitoring Tools

This directory contains tools to monitor and validate CSV processing in MinIO for the Titanic workflow using Lithops as a backend.

## Files Overview

### Processing Scripts
- **`main.py`** - Original Titanic processing script
- **`enhanced_main.py`** - Enhanced version with built-in monitoring and logging
- **`functions.py`** - Contains the `train_model` function for ML processing

### Monitoring Tools
- **`monitor_minio_processing.py`** - Comprehensive MinIO monitoring tool
- **`validate_titanic_results.py`** - Quick validation script for results
- **`README_monitoring.md`** - This file

## How to Monitor CSV Processing

### 1. Quick Validation (Recommended)
After running your Titanic processing, validate the results:

```bash
python examples/titanic/validate_titanic_results.py
```

This will:
- ✅ Check if input CSV files exist
- ✅ Analyze CSV content and data quality  
- ✅ Validate output accuracy files
- ✅ Show accuracy statistics
- ✅ Report any issues found

### 2. Comprehensive Monitoring
For detailed monitoring of all MinIO objects:

```bash
python examples/titanic/monitor_minio_processing.py
```

This provides:
- 📁 List of all input CSV files with metadata
- 📊 Detailed CSV content analysis
- 🧩 Processing artifacts (chunks, temporary files)
- 📤 Output validation with statistics
- 📋 Complete summary report

### 3. Enhanced Processing (Alternative)
Use the enhanced main script with built-in monitoring:

```bash
python examples/titanic/enhanced_main.py
```

This provides real-time monitoring during processing:
- 🚀 Pre-processing analysis
- ⏰ Timing information
- 📊 Results validation
- 💡 Next steps suggestions

## What Files Are Being Processed?

### Input Files
The script processes CSV files from the MinIO bucket under the `titanic/` prefix:
- **Location**: `test-bucket/titanic/`
- **Expected file**: `titanic.csv`
- **Required columns**: `Pclass`, `Sex`, `Age`, `SibSp`, `Parch`, `Fare`, `Survived`

### Processing Artifacts
During execution, various temporary files may be created:
- **Chunks**: `titanic-chunk-*` (if using chunking)
- **Lithops artifacts**: `lithops-*` (temporary execution files)
- **Other temporary files**: `tmp-*`, `temp-*`

### Output Files
Results are stored as:
- **Accuracy files**: `titanic-accuracy*.txt`
- **Content**: Single floating-point accuracy value (0.0 to 1.0)

## How to Check if Output is Correct

### Automated Validation
The validation script performs these checks:

1. **Input Validation**:
   - CSV files exist in the correct location
   - Required columns are present
   - Data quality analysis (missing values, etc.)

2. **Output Validation**:
   - Accuracy files exist
   - Values are in valid range [0.0, 1.0]
   - Calculate average accuracy across chunks

3. **Sanity Checks**:
   - Accuracy > 0.5 (reasonable for Titanic dataset)
   - No parsing errors
   - All required outputs present

### Manual Validation
You can also manually check:

```bash
# List all objects in bucket
python examples/titanic/monitor_minio_processing.py

# Check specific accuracy file
# The validation script will show individual accuracy values
```

### Expected Results
For the Titanic dataset, you should expect:
- **Accuracy range**: 0.6 - 0.9 (depending on data quality and chunks)
- **Average accuracy**: ~0.7-0.8 for good results
- **Processing time**: Varies based on data size and workers

## Troubleshooting

### No Input Files Found
```bash
❌ No input CSV files found in titanic/ prefix
```
**Solution**: Ensure your CSV file is uploaded to `test-bucket/titanic/`

### No Output Files
```bash
❌ No accuracy output files found
```
**Solutions**:
- Check if the processing completed successfully
- Look for error messages in the logs
- Verify Lithops and Kubernetes are working properly

### Invalid Accuracy Values
```bash
❌ Invalid accuracy: 1.5 (out of range [0,1])
```
**Solutions**:
- Check for errors in the `train_model` function
- Verify the CSV data quality
- Look for NaN or infinite values in the dataset

### Low Accuracy Results
```bash
⚠️ Warning: Average accuracy is quite low (<0.5)
```
**Solutions**:
- Check data quality (missing values, incorrect format)
- Verify feature columns are correctly named
- Check if chunks have sufficient data

## Clean Up

To remove temporary processing files:

```bash
python examples/titanic/monitor_minio_processing.py --cleanup
```

**Warning**: This will delete temporary files but preserve input CSV and final results.

## Configuration

The tools use the same configuration as your main script:
- **Config file**: `config.yaml` in the project root
- **MinIO endpoint**: Defined in config
- **Bucket**: `test-bucket` (configurable in code)

## Dependencies

The monitoring tools require:
- `minio` - MinIO Python client
- `pandas` - For CSV analysis
- `pyyaml` - For configuration parsing

Install with:
```bash
pip install minio pandas pyyaml
```
