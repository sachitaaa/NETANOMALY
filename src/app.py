
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# Import our existing prediction module
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from predict_file import load_model, predict_file

# Page configuration
st.set_page_config(
    page_title="NetAnomaly",
    page_icon="🛡️",
    layout="wide",
)

# Dashboard heading
st.title("NetAnomaly")
st.subheader("Machine Learning-Based Network Anomaly Detection System")

st.write(
    "Analyze network traffic using a trained Random Forest model."
)

st.warning(
    "Research limitation: the model may miss attacks it has not "
    "learned to recognize. A prediction of Benign does not guarantee "
    "that traffic is safe."
)

st.divider()
st.header("Upload Network Traffic Data")

uploaded_file = st.file_uploader(
    "Choose a CSV or Parquet file",
    type=["csv", "parquet"],
)

if uploaded_file is not None:
    st.write(f"**Selected file:** {uploaded_file.name}")

    if st.button("Analyze Traffic", type="primary"):
        try:
            # Read the uploaded file
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_parquet(uploaded_file)

            with st.spinner("Loading model and analyzing traffic..."):
                model = load_model()

                expected_features = list(model.feature_names_in_)
                missing_features = set(expected_features) - set(df.columns)

                if missing_features:
                    st.error(
                        "This file is missing required model features: "
                        + ", ".join(sorted(missing_features))
                    )

                else:
                    # Save uploaded data temporarily for prediction
                    temp_path = (
                        Path(__file__).resolve().parent.parent
                        / "_uploaded_temp.parquet"
                    )

                    try:
                        df.to_parquet(temp_path, index=False)
                        results = predict_file(model, temp_path)
                    finally:
                        if temp_path.exists():
                            temp_path.unlink()

                    st.success("Analysis complete!")

                    # Prediction summary
                    st.subheader("Prediction Summary")
                    counts = results["Predicted Label"].value_counts()

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Total Records",
                        f"{len(results):,}",
                    )
                    col2.metric(
                        "Benign Records",
                        f"{counts.get('Benign', 0):,}",
                    )
                    col3.metric(
                        "Potential Attacks",
                        f"{counts.get('Attack', 0):,}",
                    )

                    # Prediction chart
                    st.subheader("Traffic Classification Chart")

                    chart_data = pd.DataFrame({
                        "Prediction": ["Benign", "Attack"],
                        "Records": [
                            counts.get("Benign", 0),
                            counts.get("Attack", 0),
                        ],
                    })

                    st.bar_chart(
                        chart_data,
                        x="Prediction",
                        y="Records",
                    )

                    # Evaluate only if actual labels are available
                    if "Label" in results.columns:
                        st.divider()
                        st.subheader("Model Evaluation")
                        st.caption(
                            "These metrics compare predictions with "
                            "the dataset's actual labels."
                        )

                        y_actual = (
                            results["Label"] != "Benign"
                        ).astype(int)

                        y_predicted = (
                            results["Predicted Label"] == "Attack"
                        ).astype(int)

                        col1, col2, col3, col4 = st.columns(4)

                        col1.metric(
                            "Accuracy",
                            f"{accuracy_score(y_actual, y_predicted):.2%}",
                        )
                        col2.metric(
                            "Attack Precision",
                            f"{precision_score(y_actual, y_predicted, zero_division=0):.2%}",
                        )
                        col3.metric(
                            "Attack Recall",
                            f"{recall_score(y_actual, y_predicted, zero_division=0):.2%}",
                        )
                        col4.metric(
                            "Attack F1-score",
                            f"{f1_score(y_actual, y_predicted, zero_division=0):.2%}",
                        )

                        matrix = confusion_matrix(
                            y_actual,
                            y_predicted,
                            labels=[0, 1],
                        )

                        st.write("**Confusion Matrix**")
                        st.caption(
                            "Rows = actual class; columns = predicted class."
                        )

                        st.dataframe(
                            pd.DataFrame(
                                matrix,
                                index=["Actual Benign", "Actual Attack"],
                                columns=[
                                    "Predicted Benign",
                                    "Predicted Attack",
                                ],
                            ),
                            use_container_width=True,
                        )

                    # Results table
                    st.subheader("Prediction Results")
                    st.dataframe(
                        results.head(100),
                        use_container_width=True,
                    )

                    # Download results
                    csv_data = results.to_csv(
                        index=False
                    ).encode("utf-8")

                    st.download_button(
                        "Download All Predictions (CSV)",
                        data=csv_data,
                        file_name="netanomaly_predictions.csv",
                        mime="text/csv",
                    )

        except Exception as e:
            st.error(f"Could not analyze this file: {e}")

else:
    st.info("Upload a network traffic file to get started.")
