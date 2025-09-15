#################################################################
#################################################################

# IMPORTS

from davit.__imports__ import *

#################################################################
#################################################################

class PMAccess:

    def __init__(self, pm_server="http://pm-rest.cern.ch"):
        self.pm_server = pm_server

    def get_pm_data_header_range(self, system, className, source, fromTimestampInNanos, toTimestampInNanos):

        requestStr = "{}/v3/pmdata/header/within/range?system={}&className={}&source={}&fromTimestampInNanos={}&toTimestampInNanos={}".format(
            self.pm_server, system, className, source, fromTimestampInNanos, toTimestampInNanos)

        err = None
        df = pd.DataFrame([])

        try:
            response = requests.get(requestStr)
            response.raise_for_status()

            if response.status_code == 204:
                err = "Status Code: 204 No Content"
                print(err)
                return df, err

            df = pd.json_normalize(response.json())

        except Exception as err:
            print(err)
            return df, err

        return df, err

    def get_pm_data_duration(self, system, className, source, fromTimestampInNanos, durationInNanos):

        requestStr = "{}/v3/pmdata/within/duration?system={}&className={}&source={}&fromTimestampInNanos={}&durationInNanos={}".format(
            self.pm_server, system, className, source, fromTimestampInNanos, durationInNanos)

        err = None
        df = pd.DataFrame([])

        try:
            response = requests.get(requestStr)
            response.raise_for_status()

            if response.status_code == 204:
                err = "Status Code: 204 No Content"
                print(err)
                return df, err

            df = pd.json_normalize(response.json(), record_path=['content'])

        except Exception as err:
            print(err)
            return df, err

        return df, err

    def get_pm_data_range(self, system, className, source, fromTimestampInNanos, toTimestampInNanos):

        requestStr = "{}/v3/pmdata/within/range?system={}&className={}&source={}&fromTimestampInNanos={}&toTimestampInNanos={}".format(
            self.pm_server, system, className, source, fromTimestampInNanos, toTimestampInNanos)

        err = None
        df = pd.DataFrame([])

        try:
            response = requests.get(requestStr)
            response.raise_for_status()

            if response.status_code == 204:
                err = "Status Code: 204 No Content"
                print(err)
                return df, err

            df = pd.json_normalize(response.json(), record_path=['content'])

        except Exception as err:
            print(err)
            return df, err

        return df, err

#################################################################
#################################################################

class PostMortemQueryThread(QThread):

    #----------------------------------------------#

    # signals
    finished = pyqtSignal(tuple)

    #----------------------------------------------#

    def __init__(self, system, class_name, source, ts1, ts2, id):

        # inheritance
        super().__init__()

        # attributes
        self.system = system
        self.class_name = class_name
        self.source = source
        self.ts1 = ts1
        self.ts2 = ts2
        self.id = id

        # init pma
        self.pma = PMAccess()

        return

    #----------------------------------------------#

    def search_query(self, system, class_name, source, ts1, ts2, verbose=True):

        # perform the call
        error = None
        try:
            response_df, error = self.pma.get_pm_data_range(self.system, self.class_name, self.source, ts1, ts2)
        except Exception as xcp:
            response_df = pd.DataFrame([])
            error = xcp
            if verbose:
                print(error)

        # retrieve the id
        id = self.id

        return response_df, system, class_name, source, ts1, ts2, id, error

    #----------------------------------------------#

    def run(self):

        # run the query
        result = self.search_query(self.system, self.class_name, self.source, self.ts1, self.ts2)

        # emit the result
        self.finished.emit(result)

        return

    #----------------------------------------------#

#################################################################
#################################################################