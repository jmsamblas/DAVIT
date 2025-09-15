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

def fromBytesToString(b):

    if isinstance(b,bytes):
        b = b.decode('utf-8')

    return b

#################################################################
#################################################################

def getSystemTempDir():

    try:
        tmp_dir = tempfile.gettempdir()
    except:
        try:
            tmp_dir = os.path.expanduser('~')
        except:
            tmp_dir = ""

    return tmp_dir

#################################################################
#################################################################

def clearLayout(layout):

    if layout is not None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

#################################################################
#################################################################

def closeEventIgnore(evnt):

    evnt.ignore()

    return

#################################################################
#################################################################

def iterItems(root):

    if root is not None:
        for row in range(root.rowCount()):
            row_item = root.child(row, 0)
            if row_item.hasChildren():
                for childIndex in range(row_item.rowCount()):
                    child = row_item.child(childIndex, 0)
                    yield child

    return

#################################################################
#################################################################

def getPixelWidthFromQLabel(string, offset=30):

    w = QLabel(string).fontMetrics().boundingRect(QLabel(string).text()).width() + offset

    return w

#################################################################
#################################################################

def sort_multiple_keys(sequence, *sort_order):

    out = functools.reduce(lambda s, order: natsort.realsorted(s, key=order[0], reverse=order[1]), reversed(sort_order), sequence)

    return out


#################################################################
#################################################################

def getVersionNameFromInit(real_path):

    init_file = os.path.join(real_path, "__init__.py")

    with open(init_file, "r") as fd:
        for line in fd:
            if line.startswith("__version__"):
                version_name = ast.literal_eval(line.split("=", 1)[1].strip())

    return version_name

#################################################################
#################################################################

def NumpyFindNearest(array, value):

    array = np.array(array)
    idx = (np.abs(array-value)).argmin()
    out = array[idx]

    return out, idx

#################################################################
#################################################################

def getTabIndexByName(tab_widget, tab_name):

    for index in range(tab_widget.count()):
        if tab_widget.tabText(index) == tab_name:
            return index

    return -1

#################################################################
#################################################################

def numpy_find_nearest(array, value):

    array = np.array(array)
    idx = (np.abs(array-value)).argmin()
    out = array[idx]

    return out, idx

#################################################################
#################################################################

def get_index_type(attributes = None, df = None, return_dtype_otherwise = False):

    index_type = None
    if attributes:
        if "index" in attributes.keys():
            if attributes["index"]:
                if "IS_TIMESTAMP" in attributes["index"].keys():
                    if str(fromBytesToString(attributes["index"]["IS_TIMESTAMP"])) == "True":
                        index_type = "datetime"
                elif "IS_TIMESTEP_SERIES" in attributes["index"].keys():
                    if str(fromBytesToString(attributes["index"]["IS_TIMESTEP_SERIES"])) == "True":
                        index_type = "timestep"

    if not index_type:
        if return_dtype_otherwise:
            index_type = str(df.index.dtype)

    return index_type

#################################################################
#################################################################

def columnNameFormatting(df):

    # init
    new_cols = []
    counter = {}

    # recreate cols
    for col in df.columns:
        if col not in counter:
            new_cols.append(col)
            counter[col] = 1
        else:
            new_name = f"{col}_{counter[col]}"
            new_cols.append(new_name)
            counter[col] += 1

    # assign the new column names
    df.columns = new_cols

    # ensure all column names are strings
    df.columns = df.columns.map(str)

    return df


#################################################################
#################################################################
