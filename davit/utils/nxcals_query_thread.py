#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *

#################################################################
#################################################################

class NXCALSQueryThread(QThread):

    #----------------------------------------------#

    # signals
    finished = pyqtSignal(tuple)

    #----------------------------------------------#

    def __init__(self, ldb, query, ts1, ts2, id):

        # inheritance
        super().__init__()

        # attributes
        self.ldb = ldb
        self.query = query
        self.ts1 = ts1
        self.ts2 = ts2
        self.id = id

        return

    #----------------------------------------------#

    def search_query(self, query, ts1, ts2, verbose=True):

        # perform the call
        error = None
        try:
            response_dict = self.ldb.get(query, ts1, ts2)
        except Exception as xcp:
            response_dict = {}
            error = xcp
            if verbose:
                print(error)

        # retrieve the id
        id = self.id

        return response_dict, query, ts1, ts2, id, error

    #----------------------------------------------#

    def run(self):

        # run the query
        result = self.search_query(self.query, self.ts1, self.ts2)

        # emit the result
        self.finished.emit(result)

        return

    #----------------------------------------------#

#################################################################
#################################################################