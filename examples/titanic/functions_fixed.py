import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from flexecutor import StageContext


def train_model(ctx: StageContext) -> None:
    chunk_path = ctx.get_input_paths("titanic")[0]
    chunk = pd.read_csv(chunk_path)
    
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
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write("ERROR: Insufficient samples for training")
        return
    
    # Adjust test_size based on chunk size to avoid division by zero
    min_test_size = max(1, int(0.2 * len(X)))  # At least 1 sample for test
    min_train_size = len(X) - min_test_size
    
    if min_train_size < 1:
        print(f"Warning: Not enough samples for proper train/test split. Using single sample.")
        # For very small chunks, use the whole chunk for both training and testing
        X_train, X_test = X, X
        y_train, y_test = y, y
    else:
        # Calculate appropriate test_size to ensure we have at least 1 sample in each set
        test_size = min(0.2, min_test_size / len(X))
        test_size = max(test_size, 1 / len(X))  # Ensure at least 1 test sample
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
    
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
