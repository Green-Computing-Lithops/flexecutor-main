import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from flexecutor import StageContext


def train_model(ctx: StageContext) -> None:
    input_paths = ctx.get_input_paths("titanic")
    
    # Check if we have input paths
    if not input_paths or len(input_paths) == 0:
        print("Error: No input paths found for train_model")
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write("ERROR: No input paths found")
        return
    
    chunk_path = input_paths[0]
    
    # Check if file exists
    if not os.path.exists(chunk_path):
        print(f"Error: Input file does not exist: {chunk_path}")
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write(f"ERROR: Input file does not exist: {chunk_path}")
        return
    
    try:
        chunk = pd.read_csv(chunk_path)
    except Exception as e:
        print(f"Error reading CSV file {chunk_path}: {e}")
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write(f"ERROR: Failed to read CSV: {str(e)}")
        return
    
    # Debug: Print chunk info
    print(f"Chunk shape: {chunk.shape}")
    print(f"Chunk columns: {chunk.columns.tolist()}")
    
    features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]
    
    # Check if chunk has the required columns
    missing_cols = [col for col in features + ["Survived"] if col not in chunk.columns]
    if missing_cols:
        print(f"Missing columns: {missing_cols}")
        # Write error to output file
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write("ERROR: Missing columns in chunk")
        return
    
    # Drop rows with missing values in required columns
    chunk = chunk.dropna(subset=features + ["Survived"])
    
    # Check if chunk is empty after dropping NaN values
    if len(chunk) == 0:
        print("Warning: Chunk is empty after dropping NaN values")
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write("ERROR: Empty chunk after cleaning")
        return

    X = chunk[features]
    X = pd.get_dummies(X, columns=["Sex"], drop_first=True)
    y = chunk["Survived"]
    
    # Check if we have enough samples for train/test split
    if len(X) < 2:
        print(f"Warning: Not enough samples for train/test split. Chunk size: {len(X)}")
        # For single sample, use it for both training and testing
        if len(X) == 1:
            X_train, X_test = X, X
            y_train, y_test = y, y
        else:
            with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
                f.write("ERROR: No samples available for training")
            return
    else:
        # Safe train/test split with proper size calculation
        total_samples = len(X)
        
        # Ensure we have at least 1 sample in test set and at least 1 in train set
        min_test_samples = 1
        min_train_samples = 1
        
        # Calculate test_size ensuring both sets have at least 1 sample
        if total_samples == 2:
            # Special case: with 2 samples, use 1 for train and 1 for test
            test_size = 0.5
        else:
            # For larger datasets, use 20% for test but ensure minimums
            desired_test_samples = max(min_test_samples, int(0.2 * total_samples))
            # Ensure we don't take too many for test (leave at least 1 for train)
            max_test_samples = total_samples - min_train_samples
            actual_test_samples = min(desired_test_samples, max_test_samples)
            test_size = actual_test_samples / total_samples
        
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=None
            )
        except Exception as split_error:
            print(f"Warning: train_test_split failed ({split_error}), using alternative approach")
            # Fallback: manual split
            split_idx = max(1, int((1 - test_size) * total_samples))
            X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
            
            # Ensure we have at least one sample in each set
            if len(X_train) == 0:
                X_train, y_train = X.iloc[:1], y.iloc[:1]
                X_test, y_test = X.iloc[1:], y.iloc[1:]
            elif len(X_test) == 0:
                X_test, y_test = X.iloc[-1:], y.iloc[-1:]
                X_train, y_train = X.iloc[:-1], y.iloc[:-1]
    
    # Check if we have samples in both classes for training
    unique_classes = y_train.unique()
    if len(unique_classes) < 2:
        print(f"Warning: Only one class present in training data: {unique_classes}")
        # Still proceed with training, but note the limitation
    
    # Check if training set is empty
    if len(X_train) == 0:
        print("Error: Training set is empty")
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write("ERROR: Empty training set")
        return
    
    try:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Chunk processed successfully. Accuracy: {accuracy}")

        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write(str(accuracy))
            
    except Exception as e:
        print(f"Error during model training/prediction: {e}")
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write(f"ERROR: {str(e)}")
