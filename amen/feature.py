#!/usr/bin/env python

import six
import numpy as np
import pandas as pd

from .time import TimeSlice

# hey!  when you get to feature collections, remember that you just put a dict and have it implement.at across all members of the dict!
# and then you need a smart way to reference 2 or more things from the dict, but someone has solved that, i'm sure.

class Feature(object):
    """
    Core feature container object.  Handles indexing and time-slicing.

    Attributes
    ---------

    Methods
    ------
    at(time_slices)
        Resample the feature at the given TimeSlices
    """
    def __init__(self, data, aggregate=np.mean, base=None):
        """
        Constructor for feature object

        Parameters
        ----------
        data: pandas.DataFrame
            Time-indexed data frame of features

        aggregate: function
            resample-aggregation function or mapping

        Returns
        ------
        A Feature object

        """

        # Check that the arguments have the right types
        assert isinstance(data, pd.DataFrame)

        self.data = data
        self.aggregate = aggregate

        if base is not None:
            assert isinstance(base, Feature)

        self.base = base

    def at(self, time_slices):
        """
        Resample the data at a new time slice index.

        Parameters
        ----------
        time_slices: TimeSlice or TimeSlice collection
            The time slices at which to index this feature object

        Returns
        -------
        Feature
            The resampled feature data
        """

        if self.base is not None:
            return self.base.at(time_slices)

        if isinstance(time_slices, TimeSlice):
            time_slices = [time_slices]

        # join the time slice values
        timed_data = pd.DataFrame(columns=self.data.columns)

        # make the new data
        for sl in time_slices:
            slice_index = ((sl.time <= self.data.index) &
                           (self.data.index < sl.time + sl.duration))
            timed_data.loc[sl.time] = self.aggregate(self.data[slice_index], axis=0)

        # return the new feature object
        return Feature(data=timed_data, aggregate=self.aggregate, base=self)

