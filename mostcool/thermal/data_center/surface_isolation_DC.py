import h5py
import pandas as pd
import numpy as np

class DataCenterCGNS:
    """
    A class to handle reading and writing temperature data for a data center stored in a CGNS file.

    Attributes:
    file_path (str): Path to the CGNS file.
    temperature_path (str): Path to the temperature data within the CGNS file.
    pointlist_paths (dict): Dictionary containing paths to various point lists in the CGNS file.
    pointlists_cache (dict): Cache to store point lists for quick access.
    """

    def __init__(self, file_path):
        """
        Initializes the DataCenterCGNS object with the given file path.

        Args:
        file_path (str): Path to the CGNS file.
        """
        self.file_path = file_path
        self.temperature_path = 'Base/Zone/FlowSolution.N:1/Temperature/ data'
        self.pointlist_paths = {
            "server_in": [
                'Base/Zone/ZoneBC/vent_outlet_1_1_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_1_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_1_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_1_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_2_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_2_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_2_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_2_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_3_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_3_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_3_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_3_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_4_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_4_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_4_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_4_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_5_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_5_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_5_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_1_5_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_1_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_1_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_1_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_1_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_2_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_2_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_2_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_2_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_3_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_3_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_3_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_3_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_4_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_4_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_4_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_4_4-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_5_1-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_5_2-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_5_3-pressure-outl/PointList/ data',
                'Base/Zone/ZoneBC/vent_outlet_2_5_4-pressure-outl/PointList/ data',
            ],
            "server_out": [
                'Base/Zone/ZoneBC/mass_flow_inlet_1_1_1-massflow-/PointList/ data', 
                'Base/Zone/ZoneBC/mass_flow_inlet_1_1_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_1_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_1_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_2_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_2_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_2_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_2_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_3_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_3_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_3_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_3_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_4_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_4_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_4_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_4_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_5_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_5_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_5_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_1_5_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_1_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_1_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_1_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_1_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_2_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_2_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_2_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_2_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_3_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_3_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_3_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_3_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_4_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_4_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_4_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_4_4-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_5_1-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_5_2-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_5_3-massflow-/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet_2_5_4-massflow-/PointList/ data',
            ],
            "crah_in": [
                'Base/Zone/ZoneBC/mass_flow_inlet1-massflow-inlet/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet2-massflow-inlet/PointList/ data',
                'Base/Zone/ZoneBC/mass_flow_inlet3-massflow-inlet/PointList/ data'
            ],
            "crah_return": 'Base/Zone/ZoneBC/outlet-pressure-outlet/PointList/ data'
        }
        self.pointlists_cache = self._cache_all_pointlists()

    def _cache_all_pointlists(self):
        """
        Caches all point lists from the CGNS file.

        Returns:
        dict: A dictionary where keys are tuples of (search_string, key) and values are flattened point lists.
        """
        pointlists_cache = {}
        with h5py.File(self.file_path, 'r') as f:
            for key, paths in self.pointlist_paths.items():
                if isinstance(paths, list):
                    for path in paths:
                        search_string = path.split('/')[-3].replace('-', '_')
                        pointlist = f[path][:]
                        pointlists_cache[(search_string, key)] = np.ravel(pointlist)
                else:
                    search_string = paths.split('/')[-3].replace('-', '_')
                    pointlist = f[paths][:]
                    pointlists_cache[(search_string, key)] = np.ravel(pointlist)
        return pointlists_cache

    def calculate_temperatures(self, search_string, pointlist_type, temperature_data, stat='avg'):
        """
        Calculates the specified statistic (average, maximum, or minimum) temperatures for a given point list.

        Args:
        search_string (str): The string to search for in the cache.
        pointlist_type (str): The type of point list (server_in, server_out, crah_in, crah_return).
        temperature_data (np.array): Array of temperature data.
        stat (str): The statistic to return ('avg', 'max', 'min').

        Returns:
        float: The specified statistic temperature.
        """
        search_string = search_string.replace('-', '_')  # Normalize the search string
        cache_key = (search_string, pointlist_type)
        pointlist = self.pointlists_cache.get(cache_key, [])
        if len(pointlist) == 0:
            return None
        df_temp = pd.DataFrame({'Temperature': temperature_data})
        df_mapped = df_temp.iloc[pointlist]
        if stat == 'avg':
            return df_mapped['Temperature'].mean()
        elif stat == 'max':
            return df_mapped['Temperature'].max()
        elif stat == 'min':
            return df_mapped['Temperature'].min()
        else:
            raise ValueError(f"Unknown stat: {stat}")

    def server_inlet(self, server_inlet_location, temperature_data, stat='avg'):
        """
        Calculates and returns the specified statistic temperature for a given server inlet location.

        Args:
        server_inlet_location (str): The location of the server inlet.
        temperature_data (np.array): Array of temperature data.
        stat (str): The statistic to return ('avg', 'max', 'min').

        Returns:
        float: The specified statistic temperature.
        """
        search_string = f'vent_outlet_{server_inlet_location}-pressure-outl'
        return self.calculate_temperatures(search_string, "server_in", temperature_data, stat)

    def server_outlet(self, server_outlet_location, temperature_data, stat='avg'):
        """
        Calculates and returns the specified statistic temperature for a given server outlet location.

        Args:
        server_outlet_location (str): The location of the server outlet.
        temperature_data (np.array): Array of temperature data.
        stat (str): The statistic to return ('avg', 'max', 'min').

        Returns:
        float: The specified statistic temperature.
        """
        search_string = f'mass_flow_inlet_{server_outlet_location}-massflow-'
        return self.calculate_temperatures(search_string, "server_out", temperature_data, stat)

    def crah_inlet(self, crah_in_location, temperature_data, stat='avg'):
        """
        Calculates and returns the specified statistic temperature for a given CRAH inlet location.

        Args:
        crah_in_location (str): The location of the CRAH inlet.
        temperature_data (np.array): Array of temperature data.
        stat (str): The statistic to return ('avg', 'max', 'min').

        Returns:
        float: The specified statistic temperature.
        """
        search_string = f'mass_flow_inlet{crah_in_location}-massflow-inlet'
        return self.calculate_temperatures(search_string, "crah_in", temperature_data, stat)

    def crah_return(self, temperature_data, stat='avg'):
        """
        Calculates and returns the specified statistic temperature for the CRAH return.

        Args:
        temperature_data (np.array): Array of temperature data.
        stat (str): The statistic to return ('avg', 'max', 'min').

        Returns:
        float: The specified statistic temperature.
        """
        search_string = 'outlet_pressure_outlet'
        return self.calculate_temperatures(search_string, "crah_return", temperature_data, stat)
