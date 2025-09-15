#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *

#################################################################
#################################################################


class HDF5DataFrameHandler:

    #----------------------------------------------#

    def __init__(self, file_path: str):
        self.file_path = file_path
        return

    #----------------------------------------------#

    def time_index_to_string(self, index: pd.DatetimeIndex) -> np.array:
        part_index = index.year.to_numpy().astype(np.dtype("S"))
        for tuple_ in [
            (index.month, 2, "-"),
            (index.day, 2, "-"),
            (index.hour, 2, "T"),
            (index.minute, 2, ":"),
            (index.second, 2, ":"),
            (index.microsecond, 6, "."),
            (index.nanosecond, 3, "")
        ]:
            part_index = np.char.add(part_index, np.char.zfill(tuple_[0].astype(str), tuple_[1]) + tuple_[2])
        return part_index

    #----------------------------------------------#

    def save_dataframe_to_hdf5(self, dataframe: pd.DataFrame) -> None:
        with h5py.File(self.file_path, 'w') as h5_file:
            result_group = h5_file.create_group("dataframe")
            result_group.attrs["data_type"] = "DataFrame"
            index = dataframe.index
            is_timestamp = False
            if isinstance(index, pd.DatetimeIndex):
                index = self.time_index_to_string(index)
                is_timestamp = True
            else:
                index = index.to_numpy()
            columns_dataset = result_group.create_dataset("columns", data=dataframe.columns.to_numpy().astype(np.dtype("S")))
            index_dataset = result_group.create_dataset("index", data=index)
            index_dataset.attrs["IS_TIMESTAMP"] = is_timestamp
            data_dataset = result_group.create_dataset("data", data=dataframe.to_numpy())
            return

    #----------------------------------------------#

#################################################################
#################################################################