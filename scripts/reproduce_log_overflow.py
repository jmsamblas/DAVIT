import h5py
import numpy as np
import pyqtgraph as pg

def main():
    # --- 1. Load data from HDF5 ---
    hdf5_file = 'result_df_2.hdf5'
    data_path = '/dataframe/data'
    try:
        with h5py.File(hdf5_file, 'r') as f:
            # read the first column of your dataset
            y = f[data_path][:, 0]
    except Exception as e:
        print(f"Error reading HDF5 file: {e}")
        return

    # --- 2. Prepare x-axis ---
    x = np.arange(len(y))

    # --- 3. Plot with PyQtGraph ---
    app = pg.mkQApp()
    # pg.plot() creates a PlotWidget in its own window
    plot_win = pg.plot(x, y, pen={'color': '#0072B2', 'width': 2})
    plot_win.setWindowTitle("Simple HDF5 Data Plot")
    plot_win.setLabel('bottom', 'Index')
    plot_win.setLabel('left', 'Value')

    # start Qt event loop
    app.exec()

if __name__ == '__main__':
    main()
