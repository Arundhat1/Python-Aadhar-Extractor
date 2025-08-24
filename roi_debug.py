# roi_debug.py
import cv2
import os
import random
import json

# Path to your Aadhaar image folder
IMAGE_FOLDER = 'aadhar'

# Resize dimensions
RESIZE_W, RESIZE_H = 800, 600

# Initial ROI coordinates: (x, y, width, height)
ROIS = {
    "details": [240, 170, 400, 150],  # name + dob + gender
    "aadhar":  [280, 450, 350, 65]    # aadhar number
}

# Movement/resize step
STEP = 2

def draw_rois(img, rois, selected):
    """Draw all ROIs on an image."""
    for label, (x, y, w, h) in rois.items():
        color = (0, 255, 0) if label != selected else (0, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, label, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    return img

def main():
    global ROIS, STEP

    if not os.path.exists(IMAGE_FOLDER):
        print(f"❌ Folder not found: {IMAGE_FOLDER}")
        return

    all_images = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not all_images:
        print("❌ No images found in folder.")
        return

    sample_images = random.sample(all_images, min(15, len(all_images)))

    idx = 0
    selected_roi = "details"  # default selected box

    while True:
        img_path = os.path.join(IMAGE_FOLDER, sample_images[idx])
        img = cv2.imread(img_path)
        img = cv2.resize(img, (RESIZE_W, RESIZE_H))
        display_img = img.copy()

        draw_rois(display_img, ROIS, selected_roi)
        cv2.imshow("ROI Debug", display_img)

        key = cv2.waitKey(0) & 0xFF

        if key == ord('q'):  # quit
            break
        elif key == ord('n'):  # next image
            idx = (idx + 1) % len(sample_images)
        elif key == ord('p'):  # previous image
            idx = (idx - 1) % len(sample_images)
        elif key == ord('1'):  # select details box
            selected_roi = "details"
        elif key == ord('2'):  # select aadhar box
            selected_roi = "aadhar"
        elif key in [ord('w'), ord('s'), ord('a'), ord('d')]:
            # Move selected box
            roi = ROIS[selected_roi]
            if key == ord('w'):
                roi[1] -= STEP
            elif key == ord('s'):
                roi[1] += STEP
            elif key == ord('a'):
                roi[0] -= STEP
            elif key == ord('d'):
                roi[0] += STEP
        elif key in [ord('i'), ord('k'), ord('j'), ord('l')]:
            # Resize selected box
            roi = ROIS[selected_roi]
            if key == ord('i'):  # decrease height
                roi[3] -= STEP
            elif key == ord('k'):  # increase height
                roi[3] += STEP
            elif key == ord('j'):  # decrease width
                roi[2] -= STEP
            elif key == ord('l'):  # increase width
                roi[2] += STEP

    cv2.destroyAllWindows()

    # Save final ROIs
    with open("final_rois.json", "w") as f:
        json.dump(ROIS, f, indent=4)
    print("✅ Final ROIs saved to final_rois.json")
    print(ROIS)

if __name__ == "__main__":
    main()
