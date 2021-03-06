"""
Helper function to safely convert an array to a new data type.
"""

__docformat__ = "restructuredtext en"

import numpy

import theano

def _asarray(a, dtype, order=None):
    """Convert the input to a Numpy array.

    This function is almost identical to ``numpy.asarray``, but it should be
    used instead of its numpy counterpart when a data type is provided in
    order to perform type conversion if required.
    The reason is that ``numpy.asarray`` may not actually update the array's
    data type to the user-provided type. For more information see ticket
    http://projects.scipy.org/numpy/ticket/870.

    Currently, this issue has only been causing trouble when the target
    data type is 'int32' or 'int64', on some computers. As a result, we
    silently fix it only in this situation: if a type mismatch is detected
    with another data type, an exception is raised (if that happens, then this
    function may need to be modified to also handle this other data type).

    This function's name starts with a '_' to indicate that it is meant to be
    used internally. It is imported so as to be available directly through
        theano._asarray
    """
    if str(dtype) == 'floatX':
        dtype = theano.config.floatX
    dtype = numpy.dtype(dtype)  # Convert into dtype object.
    rval = numpy.asarray(a, dtype=dtype, order=order)
    # Note that dtype comparison must be done by comparing their `num`
    # attribute. One cannot assume that two identical data types are pointers
    # towards the same object (e.g. under Windows this appears not to be the
    # case).
    if rval.dtype.num != dtype.num:
        # Type mismatch between the data type we asked for, and the one
        # returned by numpy.asarray.
        if (dtype.num == numpy.dtype(numpy.int32).num or
                dtype.num == numpy.dtype(numpy.int64).num):
            # Silent fix.
            return rval.view(dtype=dtype)
        else:
            # Unexpected mismatch: better know what is going on!
            raise TypeError('numpy.array did not return the data type we '
                    'asked for (%s #%s), instead it returned type %s #%s: function '
                    'theano._asarray may need to be extended to handle this '
                    'data type as well.' %
                    (dtype, dtype.num, rval.dtype, rval.dtype.num))
    else:
        return rval
