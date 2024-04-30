import os
import nibabel as nib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from nilearn.image import resample_img

# Definieer de paden
fn_nifti_map = "/Users/simeonhailemariam/Documents/FN_masks"
atlas_nifti_bestand = "/Users/simeonhailemariam/Downloads/talairach (1).nii"
excel_bestand = "/Users/simeonhailemariam/Documents/excel_label.xlsx"

# Laad het atlas NIFTI-bestand en de Excel-bestanden
atlas_nifti_img = nib.load(atlas_nifti_bestand)
df_voxel_labels = pd.read_excel(excel_bestand)

# Resampling configuratie
target_affine = atlas_nifti_img.affine
target_shape = atlas_nifti_img.shape

# Loop door alle NIFTI-bestanden in de opgegeven map
for bestand in os.listdir(fn_nifti_map):
    if bestand.endswith(".nii"):
        fn_nifti_bestand = os.path.join(fn_nifti_map, bestand)
        fn_nifti_img = nib.load(fn_nifti_bestand)

        # Resample het FN NIFTI-bestand naar het formaat van de atlas
        resampled_fn_img = resample_img(fn_nifti_img,
                                        target_affine=target_affine,
                                        target_shape=target_shape,
                                        interpolation='nearest')

        resampled_fn_data = resampled_fn_img.get_fdata()

        # Vind overeenkomstige anatomische labels
        fn_voxelwaarden = atlas_nifti_img.get_fdata()[np.where(resampled_fn_data)]
        anatomische_labels = []
        for voxelwaarde in fn_voxelwaarden:
            anatomisch_label = df_voxel_labels.loc[df_voxel_labels['voxelwaarde'] == voxelwaarde]['anatomisch label'].values
            anatomische_labels.extend(anatomisch_label)

        # Bereken de frequentie van elk anatomisch label
        label_frequentie = pd.Series(anatomische_labels).value_counts()

        # Filter labels met een frequentie van minstens 5%
        label_frequentie = label_frequentie[label_frequentie >= len(anatomische_labels) * 0.05]

        # Plot cirkeldiagram als er minstens één label is
        if not label_frequentie.empty:
            plt.figure(figsize=(8, 8))
            label_frequentie.plot(kind='pie', autopct='%1.1f%%', startangle=140)
            plt.title(f'Percentage van elk anatomisch label voor {bestand}')
            plt.ylabel('')  # Verwijder de y-label, omdat dit niet relevant is voor een cirkeldiagram
            plt.show()

            # Afdrukken van de gevonden anatomische labels
            print(f"Anatomische labels voor {bestand}:")
            for label in anatomische_labels:
                print(label)
            print('-----------------------------------------------------------------')

        # Plot de atlas-NIFTI-afbeelding met FN-overlay
        plt.figure(figsize=(10, 10))
        plt.imshow(atlas_nifti_img.get_fdata()[:, :, target_shape[2] // 2], cmap='gray')
        plt.title(f'Atlas NIFTI met {bestand} FN-overlay')
        plt.colorbar(label='Voxelwaarde')
        plt.imshow(resampled_fn_data[:, :, target_shape[2] // 2], cmap='jet', alpha=0.5)
        plt.colorbar(label='Voxelwaarde FN-overlay')
        plt.show()
        
        
        
