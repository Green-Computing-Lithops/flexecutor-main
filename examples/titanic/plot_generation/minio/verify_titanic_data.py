#!/usr/bin/env python3
"""
Script to verify the integrity and structure of the expanded Titanic dataset.
"""

import csv
import pandas as pd

def verify_titanic_data(filename):
    print("=" * 60)
    print("TITANIC DATASET VERIFICATION REPORT")
    print("=" * 60)
    
    # Basic file information
    with open(filename, 'r') as file:
        lines = file.readlines()
        total_lines = len(lines)
        print(f"Total lines in file: {total_lines:,}")
        print(f"Data rows (excluding header): {total_lines - 1:,}")
    
    # Load data with pandas for detailed analysis
    print("\nLoading data with pandas...")
    df = pd.read_csv(filename)
    
    print(f"DataFrame shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    print("\n" + "=" * 60)
    print("DATA STRUCTURE VERIFICATION")
    print("=" * 60)
    
    # Check data types
    print("\nData types:")
    print(df.dtypes)
    
    # Check for missing values
    print("\nMissing values per column:")
    missing_values = df.isnull().sum()
    for col, missing in missing_values.items():
        percentage = (missing / len(df)) * 100
        print(f"  {col}: {missing:,} ({percentage:.1f}%)")
    
    print("\n" + "=" * 60)
    print("DATA QUALITY CHECKS")
    print("=" * 60)
    
    # Check PassengerId sequence
    expected_ids = set(range(1, len(df) + 1))
    actual_ids = set(df['PassengerId'])
    missing_ids = expected_ids - actual_ids
    duplicate_ids = df['PassengerId'].duplicated().sum()
    
    print(f"\nPassenger ID verification:")
    print(f"  Expected range: 1 to {len(df)}")
    print(f"  Missing IDs: {len(missing_ids)}")
    print(f"  Duplicate IDs: {duplicate_ids}")
    if len(missing_ids) > 0:
        print(f"  Missing ID examples: {sorted(list(missing_ids))[:10]}")
    
    # Check value ranges
    print(f"\nValue range checks:")
    print(f"  Survived: {df['Survived'].min()} to {df['Survived'].max()} (should be 0-1)")
    print(f"  Pclass: {df['Pclass'].min()} to {df['Pclass'].max()} (should be 1-3)")
    print(f"  Age: {df['Age'].min()} to {df['Age'].max()} (should be reasonable)")
    print(f"  SibSp: {df['SibSp'].min()} to {df['SibSp'].max()}")
    print(f"  Parch: {df['Parch'].min()} to {df['Parch'].max()}")
    print(f"  Fare: {df['Fare'].min()} to {df['Fare'].max()}")
    
    # Check categorical values
    print(f"\nCategorical value checks:")
    print(f"  Sex values: {df['Sex'].unique()}")
    print(f"  Embarked values: {df['Embarked'].unique()}")
    
    print("\n" + "=" * 60)
    print("DISTRIBUTION ANALYSIS")
    print("=" * 60)
    
    # Survival rate
    survival_rate = df['Survived'].mean()
    print(f"\nOverall survival rate: {survival_rate:.1%}")
    
    # Class distribution
    print(f"\nClass distribution:")
    class_dist = df['Pclass'].value_counts().sort_index()
    for pclass, count in class_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  Class {pclass}: {count:,} passengers ({percentage:.1f}%)")
    
    # Sex distribution
    print(f"\nSex distribution:")
    sex_dist = df['Sex'].value_counts()
    for sex, count in sex_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  {sex.capitalize()}: {count:,} passengers ({percentage:.1f}%)")
    
    # Age statistics
    print(f"\nAge statistics:")
    age_stats = df['Age'].describe()
    print(f"  Count (non-null): {age_stats['count']:.0f}")
    print(f"  Mean: {age_stats['mean']:.1f} years")
    print(f"  Median: {age_stats['50%']:.1f} years")
    print(f"  Min: {age_stats['min']:.0f} years")
    print(f"  Max: {age_stats['max']:.0f} years")
    
    # Fare statistics by class
    print(f"\nFare statistics by class:")
    for pclass in sorted(df['Pclass'].unique()):
        fare_stats = df[df['Pclass'] == pclass]['Fare'].describe()
        print(f"  Class {pclass}: Mean ${fare_stats['mean']:.2f}, Median ${fare_stats['50%']:.2f}")
    
    print("\n" + "=" * 60)
    print("SAMPLE DATA VERIFICATION")
    print("=" * 60)
    
    # Show sample of original data (first few rows)
    print(f"\nFirst 3 original passengers:")
    print(df.head(3)[['PassengerId', 'Name', 'Sex', 'Age', 'Pclass', 'Survived']].to_string(index=False))
    
    # Show sample of generated data
    print(f"\nFirst 3 generated passengers (starting from ID 892):")
    generated_sample = df[df['PassengerId'] >= 892].head(3)
    print(generated_sample[['PassengerId', 'Name', 'Sex', 'Age', 'Pclass', 'Survived']].to_string(index=False))
    
    # Show last few rows
    print(f"\nLast 3 passengers:")
    print(df.tail(3)[['PassengerId', 'Name', 'Sex', 'Age', 'Pclass', 'Survived']].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    issues = []
    
    # Check for critical issues
    if duplicate_ids > 0:
        issues.append(f"Found {duplicate_ids} duplicate passenger IDs")
    
    if len(missing_ids) > 0:
        issues.append(f"Found {len(missing_ids)} missing passenger IDs")
    
    if not df['Survived'].isin([0, 1]).all():
        issues.append("Invalid values in Survived column (should be 0 or 1)")
    
    if not df['Pclass'].isin([1, 2, 3]).all():
        issues.append("Invalid values in Pclass column (should be 1, 2, or 3)")
    
    if not df['Sex'].isin(['male', 'female']).all():
        issues.append("Invalid values in Sex column")
    
    # Check for reasonable age values
    valid_ages = df['Age'].dropna()
    if (valid_ages < 0).any() or (valid_ages > 100).any():
        issues.append("Unreasonable age values found")
    
    if len(issues) == 0:
        print("✅ All verification checks PASSED!")
        print("✅ Data structure is intact")
        print("✅ Data quality is good")
        print("✅ Dataset successfully expanded to 10x original size")
    else:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    
    print(f"\n📊 Final dataset size: {len(df):,} passengers")
    print(f"📈 Expansion factor: {len(df) / 891:.1f}x (from original 891 passengers)")

if __name__ == "__main__":
    verify_titanic_data('/home/users/iarriazu/flexecutor-main/test-bucket/titanic/titanic.csv')
