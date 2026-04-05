from google import genai
from PIL import Image
import os
import json
import time
from dotenv import load_dotenv

print("🚀 Script started")

# Load environment variables
load_dotenv()

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Folders
IMAGE_FOLDER = "images"
OUTPUT_FOLDER = "outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Prompt
PROMPT = """
Return ONLY valid JSON. Do not add explanations.

{
  "category": "",
  "objects_detected": [],
  "text": "",
  "tags": [],
  "summary": ""
}
"""

# Process one image
def process_image(image_path, image_id):
    for attempt in range(3):
        try:
            print(f"📸 Processing {image_id}...")

            img = Image.open(image_path)

            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[PROMPT, img]
            )

            text_output = response.text.strip()

            try:
                result = json.loads(text_output)
            except:
                print("⚠️ Invalid JSON, saving raw output")
                result = {
                    "error": "Invalid JSON",
                    "raw_output": text_output
                }

            result["image_id"] = image_id

            output_path = os.path.join(OUTPUT_FOLDER, f"{image_id}.json")
            with open(output_path, "w") as f:
                json.dump(result, f, indent=4)

            print(f"✅ Saved: {output_path}")
            return

        except Exception as e:
            print(f"❌ Attempt {attempt+1} failed: {e}")
            time.sleep(5)

    # Fallback (important for submission)
    print(f"🚨 Using fallback for {image_id}")
    result = {
        "image_id": image_id,
        "category": "unknown",
        "objects_detected": [],
        "text": "",
        "tags": [],
        "summary": "Fallback result due to API failure"
    }

    output_path = os.path.join(OUTPUT_FOLDER, f"{image_id}.json")
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)


# MAIN EXECUTION
if __name__ == "__main__":
    print("🚀 Starting main loop")

    files = os.listdir(IMAGE_FOLDER)
    print("📂 Files found:", files)

    if not files:
        print("⚠️ No images found in 'images/' folder")

    for i, filename in enumerate(files):
        print(f"➡️ Checking file: {filename}")

        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            print(f"✅ Valid image found: {filename}")

            image_path = os.path.join(IMAGE_FOLDER, filename)
            image_id = f"img_{i+1:03d}"

            process_image(image_path, image_id)

            break  # 🔥 Only process ONE image for now

    print("🏁 Script finished")