# FlexExecutor Environment Setup Guide

This guide explains how to properly configure environment variables for FlexExecutor, replacing hardcoded AWS credentials with secure environment variable management.

## 🔧 Quick Setup

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Edit Your Credentials
Open `.env` and replace the placeholder values with your actual AWS credentials:

```bash
# AWS Credentials - Replace with your actual credentials


# AWS Configuration
AWS_DEFAULT_REGION=us-east-1
```

### 3. Load Environment Variables

#### Option A: Using the Configuration Loader (Recommended)
```bash
# Activate virtual environment first
source venv310/bin/activate

# Process configuration with environment variables
python config_loader.py
```

#### Option B: Using the Shell Script
```bash
# Make executable (if not already)
chmod +x setup_env.sh

# Run the setup script
./setup_env.sh

# Or source it to load variables in current shell
source setup_env.sh
```

#### Option C: Using Python Utility
```bash
python load_env.py
```

#### Option D: Manual Export
```bash
# Load environment variables manually
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_SESSION_TOKEN="your_session_token"
export AWS_DEFAULT_REGION="us-east-1"
export LITHOPS_CONFIG_FILE="config_aws.yaml"
```

## 📁 File Structure

```
flexecutor-main/
├── .env                    # Your actual credentials (DO NOT COMMIT)
├── .env.example           # Template file (safe to commit)
├── setup_env.sh          # Shell script to load environment
├── load_env.py           # Python utility to load environment
├── config_loader.py      # Configuration processor with os.getenv() support
├── config_aws.yaml       # Config with os.getenv() calls
├── config_processed.yaml # Generated config with resolved values
└── README_ENV_SETUP.md   # This guide
```

## 🔒 Security Improvements

### Before (❌ Insecure)
```yaml
# config_aws.yaml


### After (✅ Secure)
```yaml
# config_aws.yaml
aws:
    # AWS credentials loaded from environment variables using os.getenv()
    AWS_ACCESS_KEY_ID: "os.getenv('AWS_ACCESS_KEY_ID')"
    AWS_SECRET_ACCESS_KEY: "os.getenv('AWS_SECRET_ACCESS_KEY')"
    AWS_SESSION_TOKEN: "os.getenv('AWS_SESSION_TOKEN')"
    region: us-east-1
```

**Note:** The `config_loader.py` processes these `os.getenv()` calls and replaces them with actual environment variable values, generating a `config_processed.yaml` file with resolved credentials.

## 🚀 Usage Examples

### Running FlexExecutor Applications

After setting up your environment, you can run applications normally:

```bash
# Setup environment first
source setup_env.sh

# Run examples
python examples/montecarlo_pi_estimation/main.py
python examples/titanic/main.py
python examples/video/main.py
python examples/ml/main.py
```

### Validating Your Setup

Use the Python utility to validate your configuration:

```bash
python load_env.py
```

Expected output:
```
FlexExecutor Environment Loader
========================================
✓ Loaded 8 environment variables from .env
✓ AWS credentials validation passed

=== Environment Variables Status ===

AWS Configuration:
  AWS_ACCESS_KEY_ID: ASIA4MTW...HJ6K
  AWS_SECRET_ACCESS_KEY: iHUaY1TM...2Pn
  AWS_SESSION_TOKEN: IQoJb3Jp...RQHg
  AWS_DEFAULT_REGION: us-east-1

Other Configuration:
  LITHOPS_CONFIG_FILE: config_aws.yaml
  DOCKER_ENGINE: podman

✅ Environment setup complete!
You can now run your FlexExecutor applications.
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Missing .env file
```bash
Error: .env not found!
```
**Solution:** Copy the template file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

#### 2. Placeholder values not replaced
```bash
Error: Please replace placeholder values for: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
```
**Solution:** Edit `.env` and replace `your_aws_access_key_here` with actual values.

#### 3. Permission denied on setup_env.sh
```bash
Permission denied: ./setup_env.sh
```
**Solution:** Make the script executable:
```bash
chmod +x setup_env.sh
```

#### 4. Virtual environment not found
```bash
Warning: No virtual environment found
```
**Solution:** Create and activate a virtual environment:
```bash
python -m venv venv310
source venv310/bin/activate
pip install -r requirements.txt
```

### Environment Variable Priority

FlexExecutor will look for AWS credentials in this order:
1. Environment variables (`.env` file or exported variables)
2. AWS credentials file (`~/.aws/credentials`)
3. AWS config file (`~/.aws/config`)
4. IAM roles (if running on EC2)

## 🔐 Security Best Practices

### ✅ Do's
- ✅ Use `.env` files for local development
- ✅ Keep `.env` in `.gitignore`
- ✅ Use IAM roles in production
- ✅ Rotate credentials regularly
- ✅ Use temporary credentials when possible
- ✅ Validate environment setup before running applications

### ❌ Don'ts
- ❌ Never commit `.env` files to version control
- ❌ Don't hardcode credentials in source code
- ❌ Don't share credentials in plain text
- ❌ Don't use long-lived credentials in production
- ❌ Don't ignore credential validation errors

## 📚 Additional Resources

- [AWS CLI Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [AWS Security Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Lithops AWS Configuration](https://lithops-cloud.github.io/docs/source/compute_config/aws_lambda.html)

## 🆘 Getting Help

If you encounter issues:

1. **Check your environment setup:**
   ```bash
   python load_env.py
   ```

2. **Validate AWS credentials:**
   ```bash
   aws sts get-caller-identity
   ```

3. **Check Lithops configuration:**
   ```bash
   lithops test -b aws_lambda
   ```

4. **Review logs for detailed error messages**

---

**⚠️ Important:** Never commit your `.env` file to version control. It contains sensitive credentials that should be kept private.
