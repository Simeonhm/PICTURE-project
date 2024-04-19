import os
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt

def pad_to_match(data1, data2):
    pad_width = [(0, max(0, data2.shape[i] - data1.shape[i])) for i in range(3)]
    data1_padded = np.pad(data1, pad_width, mode='constant', constant_values=0)
    return data1_padded

def dice_coefficient(y_true, y_pred):
    intersection = np.sum(y_true * y_pred)
    return (2. * intersection) / (np.sum(y_true) + np.sum(y_pred))

def jaccard_index(y_true, y_pred):
    intersection = np.sum(y_true * y_pred)
    union = np.sum(y_true) + np.sum(y_pred) - intersection
    return intersection / union

def compute_confusion_matrix(y_true, y_pred):
    TP = np.sum((y_true == 1) & (y_pred == 1))
    TN = np.sum((y_true == 0) & (y_pred == 0))
    FP = np.sum((y_true == 0) & (y_pred == 1))
    FN = np.sum((y_true == 1) & (y_pred == 0))
    return TP, TN, FP, FN

def compute_metrics(TP, TN, FP, FN):
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    return accuracy, sensitivity, specificity

def get_anatomical_label(atlas, fn_mask):
    label_ids = np.unique(atlas[fn_mask])
    return label_ids

def analyze_slices(data, data2, atlas_data, slice_index):
    dice_score = dice_coefficient(data2, data)
    jaccard_score = jaccard_index(data2, data)
    TP, TN, FP, FN = compute_confusion_matrix(data2, data)
    accuracy, sensitivity, specificity = compute_metrics(TP, TN, FP, FN)
    
    # Identificeer FN's en haal anatomische labels op
    fn_mask = (data2 == 1) & (data == 0)
    anatomical_labels = get_anatomical_label(atlas_data[:, :, slice_index], fn_mask)
    
    print(f"Slice {slice_index} - DICE Score: {dice_score:.4f}, Jaccard Index: {jaccard_score:.4f}")
    print(f"Confusion Matrix: TP={TP}, TN={TN}, FP={FP}, FN={FN}")
    print(f"Metrics: Accuracy={accuracy:.4f}, Sensitivity={sensitivity:.4f}, Specificity={specificity:.4f}")
    print(f"Anatomische labels voor FN's: {anatomical_labels}")
    
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.imshow(data.T, cmap='gray', origin='lower')
    plt.title(f'Slice {slice_index} - AI Segmentatie')
    plt.colorbar()
    
    plt.subplot(1, 2, 2)
    plt.imshow(data2.T, cmap='gray', origin='lower')
    plt.title(f'Slice {slice_index} - Expert Segmentatie')
    plt.colorbar()
    plt.show()

# Je bestaande match_and_compare functie aanpassen om de atlas te gebruiken
def match_and_compare(ai_dir, expert_base_dir, atlas_path):
    atlas_img = nib.load(atlas_path)
    atlas_data = atlas_img.get_fdata()

    ai_files = [f for f in os.listdir(ai_dir) if f.endswith('_segmentation.nii')]
    
    for ai_file in ai_files:
        patient_id = ai_file.split('_segmentation.nii')[0]
        expert_file = patient_id + '_modified_seg.nii.gz'
        expert_path = os.path.join(expert_base_dir, patient_id, expert_file)
        
        if os.path.exists(expert_path):
            print(f"Analyse van {ai_file} en {expert_file}")
            img = nib.load(os.path.join(ai_dir, ai_file))
            data = img.get_fdata()
            data = np.flip(data, axis=0)
            
            img2 = nib.load(expert_path)
            data2 = img2.get_fdata()
            data2 = np.flip(data2, axis=1)
            
            if data.shape != data2.shape:
                if np.prod(data.shape) < np.prod(data2.shape):
                    data = pad_to_match(data, data2)
                else:
                    data2 = pad_to_match(data2, data)
            
            num_slices = min(data.shape[2], data2.shape[2])
            for slice_index in range(num_slices):
                slice_data = data[:, :, slice_index]
                slice_data2 = data2[:, :, slice_index]
                if np.any(slice_data == 1) or np.any(slice_data2 == 1):
                    analyze_slices(slice_data, slice_data2, atlas_data, slice_index)
        else:
            print(f"Geen overeenkomende expertsegmentatie gevonden voor {patient_id}")

atlas_path = 'path_to_your_atlas.nii'  # Zorg dat je dit pad vervangt door het juiste pad naar je atlas.
ai_dir = '/Users/simeonhailemariam/Documents'
expert_base_dir = '/Users/simeonhailemariam/Downloads/archive/BraTS2021_Training_Data'
match_and_compare(ai_dir, expert_base_dir)
