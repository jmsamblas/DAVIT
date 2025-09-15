import os
import time
import h5py
import numpy as np
from datetime import datetime

# Configuration
OUTPUT_DIR = 'h5_output'
SLEEP_INTERVAL = 10  # seconds

def ensure_dir(path):
    """Create directory if it doesn't exist."""
    if not os.path.isdir(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def create_h5_file(dir_path, idx):
    """
    Create a small HDF5 file named file_{idx}.h5 in dir_path,
    containing a dummy dataset with the current timestamp.
    """
    filename = os.path.join(dir_path, f"file_{idx:04d}.h5")
    with h5py.File(filename, 'w') as f:
        # Example: store a scalar dataset 'timestamp' as an ISO string vs. bytes
        ts = datetime.utcnow().isoformat().encode('utf-8')
        dt = h5py.string_dtype(encoding='utf-8')
        ds = f.create_dataset('timestamp', data=np.array(ts, dtype=dt))
        # Optionally add some random data:
        f.create_dataset('random', data=np.random.random(size=(5,)))
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Created {filename}")

def main():
    ensure_dir(OUTPUT_DIR)
    idx = 0
    print(f"Starting to generate HDF5 files every {SLEEP_INTERVAL} seconds in '{OUTPUT_DIR}'")
    try:
        while True:
            create_h5_file(OUTPUT_DIR, idx)
            idx += 1
            time.sleep(SLEEP_INTERVAL)
    except KeyboardInterrupt:
        print("\nInterrupted by user — exiting.")

if __name__ == '__main__':
    main()

