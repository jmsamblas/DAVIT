"""
Usage Example:
--------------
To run this script from the command line, use a command similar to the following:

python scripts/regroup_big_files.py /user/martinja/apps/davit/hdf5_test_files/super_big_test/bigger2.h5 /user/martinja/apps/davit/hdf5_test_files/super_big_test/bigger2_new.h5 --group FFT_Data --size 1000

This command organizes the datasets in the 'FFT_Data' group of the original file into subgroups of 1000 datasets,
each subgroup being named directly as a timestamp range (e.g. '1729024179.385_to_1729024259.225'), and writes the result to the new file.
"""

import h5py
import os
import sys
import argparse
from tqdm import tqdm

def extract_timestamp(dataset_name):
    """
    Extracts the timestamp from the dataset name.
    Expected format: FFT_H_1730514505.785_0 or FFT_V_1730514505.785_0
    """
    try:
        parts = dataset_name.split('_')
        return float(parts[2])
    except (IndexError, ValueError):
        print(f"Warning: Unable to extract timestamp from dataset name '{dataset_name}'. Assigning timestamp=0.")
        return 0.0

def organize_hdf5_by_timestamp(original_file_path, new_file_path, group_name='FFT_Data',
                               group_size=1000, verbose=False):
    """
    Organizes datasets within an HDF5 group into timestamp-based subgroups
    and writes them to a new HDF5 file under a main group.

    Parameters:
      original_file_path (str): Path to the original HDF5 file.
      new_file_path (str): Path to the new HDF5 file to be created.
      group_name (str): Name of the group containing datasets to organize.
      group_size (int): Number of datasets per timestamp subgroup.
      verbose (bool): If True, prints detailed status messages; otherwise uses tqdm progress bars.
    """
    if not os.path.isfile(original_file_path):
        print(f"Error: Original file '{original_file_path}' does not exist.")
        sys.exit(1)

    try:
        with h5py.File(original_file_path, 'r') as orig_f, h5py.File(new_file_path, 'w') as new_f:
            if group_name not in orig_f:
                print(f"Error: Group '{group_name}' not found in the original file.")
                return

            fft_data_orig = orig_f[group_name]
            dataset_names = list(fft_data_orig.keys())

            if not dataset_names:
                print(f"No datasets found in group '{group_name}' of the original file.")
                return

            if verbose:
                print(f"Found {len(dataset_names)} datasets in group '{group_name}' of the original file.")

            # Sort dataset names by timestamp.
            sorted_datasets = sorted(dataset_names, key=extract_timestamp)

            num_groups = (len(sorted_datasets) + group_size - 1) // group_size
            if verbose:
                print(f"Organizing into {num_groups} timestamp subgroups with up to {group_size} datasets each.")

            # Create the main group in the new file.
            main_group = new_f.create_group(group_name)
            if verbose:
                print(f"Created main group '{group_name}' in the new file.")

            # Iterate over partitions and create timestamp-based groups (one tqdm for outer loop only).
            for i in tqdm(range(num_groups), desc="Processing timestamp groups", unit="group", disable=verbose):
                # Determine the current batch of datasets.
                start_idx = i * group_size
                end_idx = start_idx + group_size
                current_batch = sorted_datasets[start_idx:end_idx]

                # Extract timestamps for the current batch and compute the min and max.
                timestamps = [extract_timestamp(ds_name) for ds_name in current_batch]
                min_timestamp = min(timestamps)
                max_timestamp = max(timestamps)

                # Define the timestamp-based subgroup name.
                timestamp_group_name = f"{min_timestamp}_to_{max_timestamp}"
                # Create the subgroup under the main group.
                ts_group = main_group.create_group(timestamp_group_name)
                if verbose:
                    print(f"Created timestamp group '{timestamp_group_name}' with {len(current_batch)} datasets.")

                # Iterate over the current batch of datasets.
                for ds_name in current_batch:
                    src_path = f"{group_name}/{ds_name}"
                    if ds_name not in fft_data_orig:
                        if verbose:
                            print(f"Warning: Dataset '{ds_name}' not found in '{group_name}'. Skipping.")
                        continue
                    try:
                        # Copy dataset to the timestamp-based subgroup.
                        orig_f.copy(src_path, ts_group, name=ds_name)
                    except Exception as e:
                        if verbose:
                            print(f"Error copying '{src_path}' to '{group_name}/{timestamp_group_name}/{ds_name}': {e}")

            if verbose:
                print("Organization into new file complete.")

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Organize HDF5 datasets into timestamp-based subgroups (without part subgroups) and create a new HDF5 file.'
    )
    parser.add_argument('original_file', type=str, help='Path to the original HDF5 file.')
    parser.add_argument('new_file', type=str, help='Path to the new HDF5 file to be created.')
    parser.add_argument('--group', type=str, default='FFT_Data', help='Name of the group containing datasets.')
    parser.add_argument('--size', type=int, default=1000, help='Number of datasets per timestamp subgroup.')
    parser.add_argument('--verbose', action="store_true", help='Increase output verbosity.')

    args = parser.parse_args()
    organize_hdf5_by_timestamp(args.original_file, args.new_file, args.group, args.size, args.verbose)
