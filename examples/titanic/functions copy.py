import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from flexecutor import StageContext


def train_model(ctx: StageContext) -> None:
    chunk_path = ctx.get_input_paths("titanic")[0]
    chunk = pd.read_csv(chunk_path)
    features = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Fare"]
    chunk = chunk.dropna(subset=features + ["Survived"])

    # Check if we have enough data after dropping NaN values
    if len(chunk) < 2:
        print(f"Warning: Chunk has insufficient data ({len(chunk)} rows), writing default accuracy")
        with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
            f.write("0.0")
        return

    X = chunk[features]
    X = pd.get_dummies(X, columns=["Sex"], drop_first=True)
    y = chunk["Survived"]

    # Check if we have enough data for train_test_split
    if len(X) < 5:  # Need at least 5 samples for meaningful split
        print(f"Warning: Insufficient data for train/test split ({len(X)} samples), using all data for training")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)
    else:
        # Ensure test_size doesn't result in empty test set
        test_size = max(0.2, 1.0 / len(X))  # At least 1 sample in test set
        if test_size >= 1.0:
            test_size = 0.2
            
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

    with open(ctx.next_output_path("titanic-accuracy"), "w") as f:
        f.write(str(accuracy))
