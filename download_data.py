import os
import shutil
import kagglehub

# 1. Download the dataset using your token env variable
# Dataset URL: https://kaggle.com
print("Connecting to Kaggle and downloading dataset...")
downloaded_path = kagglehub.dataset_download(
    "nelgiriyewithana/top-spotify-songs-2023")

print(f"Dataset downloaded to temporary cache: {downloaded_path}")

# 2. Find the CSV and copy it safely into your project data folder
for file in os.listdir(downloaded_path):
    if file.endswith('.csv'):
        old_file_path = os.path.join(downloaded_path, file)
        new_file_path = os.path.join("data", "spotify_data.csv")

        # Ensure target folder exists just in case
        os.makedirs("data", exist_ok=True)

        # Copy the file
        shutil.copy(old_file_path, new_file_path)
        print(f"🎯 Success! Moved {file} to data/spotify_data.csv")
        break
