import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    accuracy_score,
    recall_score,
    precision_score,
    f1_score,
    classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================
# LOAD LABELS
# ==========================
df = pd.read_csv("labels.csv")

true_labels = df["TRUE"].values
predicted_labels = df["PRED"].values

# ==========================
# VALID POSES ONLY
# ==========================
valid_poses = [
    "Tree Pose",
    "Downward Dog Pose",
    "Goddess Pose",
    "Lotus Pose",
    "Butterfly Pose",
    "Easy Pose"
]

# Remove rows where TRUE is not a valid pose (safety)
filtered_df = df[df["TRUE"].isin(valid_poses)]

true_labels = filtered_df["TRUE"].values
predicted_labels = filtered_df["PRED"].values

# Confusion matrix should ONLY include the valid yoga poses
labels = valid_poses

# ==========================
# METRICS
# ==========================
cm = confusion_matrix(true_labels, predicted_labels, labels=labels)
acc = accuracy_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels, average='macro', zero_division=0)
precision = precision_score(true_labels, predicted_labels, average='macro', zero_division=0)
f1 = f1_score(true_labels, predicted_labels, average='macro', zero_division=0)

print("\n========== METRICS ==========")
print("Accuracy:", acc)
print("Recall:", recall)
print("Precision:", precision)
print("F1 Score:", f1)

print("\n========== PER-POSE REPORT ==========")
print(classification_report(true_labels, predicted_labels, labels=labels, zero_division=0))

# ==========================
# CONFUSION MATRIX HEATMAP
# ==========================
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, cmap="Blues", fmt="d",
            xticklabels=labels, yticklabels=labels)
plt.title("Confusion Matrix (Heatmap)")
plt.xlabel("Predicted")
plt.ylabel("True")
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()


# ==========================
# REAL ACCURACY LINE GRAPH (TRUE SYSTEM PERFORMANCE)
# ==========================

pose_names = []
pose_acc_values = []

for pose in labels:
    pose_df = filtered_df[filtered_df["TRUE"] == pose]

    if len(pose_df) > 0:
        correct = (pose_df["TRUE"] == pose_df["PRED"]).sum()
        acc_val = correct / len(pose_df)
        pose_acc_values.append(acc_val)
    else:
        pose_acc_values.append(0)

    pose_names.append(pose)

plt.figure(figsize=(8, 5))
plt.plot(pose_names, pose_acc_values, marker='o', label='Accuracy')
plt.title("System Accuracy per Pose")
plt.xlabel("Pose Name")
plt.ylabel("Accuracy")
plt.ylim(0, 1.05)
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

# ==========================
# OVERALL METRICS BAR CHART (SOFT COLORS)
# ==========================

overall_metrics = {
    "Accuracy": acc,
    "Precision": precision,
    "Recall": recall,
    "F1 Score": f1
}

soft_colors = ['#7DA6F7', '#7FD1AE', '#F6C27A', '#F28B82']  # soft pastel colors

plt.figure(figsize=(7, 5))
plt.bar(overall_metrics.keys(), overall_metrics.values(), color=soft_colors)
plt.title("Overall System Performance Metrics")
plt.ylabel("Value")
plt.ylim(0, 1)
plt.grid(axis='y', linestyle='--', alpha=0.4)

# Add percentage labels
for key, value in overall_metrics.items():
    plt.text(key, value + 0.02, f"{value*100:.1f}%", ha='center')

plt.tight_layout()
plt.show()




