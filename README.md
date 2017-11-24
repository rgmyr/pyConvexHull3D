# pyConvexHull3D

`dcel.py`: Provides the doubly-connected edge list, Vertex, hEdge, and Face classes. `DCEL` is a `dict`-based implementation, adapted from the `list`-based python2 implementation at: [https://github.com/Ylannl/pydcel](https://github.com/Ylannl/pydcel). Python version >=3.6 is strongly recommended, as the implementation here assumes that dictionaries preserve insertion order. In theory, it should work with key-ordered dicts as well, but this has not been tested.

`hull3D.py`: Provides the `ConvexHull3D` algorithm class with visualization capabilities.

`test.py`: Runs tests and prints output.

## Dependencies  

Aside from standard library modules `collections` and `itertools`, running the algorithm requires `numpy` and `matplotlib`. Running `test.py` requires `scipy`, as the solutions are tested against those produced by `scipy.spatial.ConvexHull()` (which calls the `QHull` library). 

## Future Updates

Currently `pyConvexHull3D` produces the exact solution for sets of points in general position (in the sense of no three points on the hull being colinear). This is almost always the case when using float coordinates, or integer coordinates in a bounding cube that is large relative to the number of points. When there are colinear points on the hull, the vertices reported by `QHull` are a proper subset of those reported by `pyConvexHull3D`.

## Usage

Simple usage example:
```Python
from hull3D import ConvexHull3d
import numpy as np

pts = np.random.randint(-100, 100, (100,3))

# Showing default parameters
Hull = ConvexHull3D(pts, run=True, preproc=True, make_frames=False, frames_dir='./frames/')

# To get vertex objects:
vertices = Hull.DCEL.vertexDict.values()

# To get indices:
pts = Hull.getPts()    # if preproc=True
hull_vertices = pts[Hull.getVertexIndices()]
```

Parameter explanations:

`pts`
- Should be type np.array with shape `(n, 3)`.

`preproc=True`
- Set to `False` to disable preprocessing function, which swaps rows in `pts` such that Hull(`i=6`) is more likely to be large.

`run=True`         
- Set to `False` to run full algorithm at a later time by calling `Hull.runAlgorithm()`.

`make_frames=False`
- Set to `True` to output png frames at each step to `frame_dir`.

`frames_dir='./frames/'`
- Set to change directory where frames are saved if `make_frames=True`. This directory should exist.

Call `Hull.generateImage(show=True)` to generate and output an image using `plt.show()` rather than saving a png file. If `make_frames=False`, then this method will use `plt.show()` by default.

If `preproc=True` and you want to compare output with another algorithm, call `Hull.getPts()` to get the points in the preprocessed order used by `Hull`.

The included `example.mp4` movie for 100 randomly distributed integer points was produced with `ffmpeg`:
```
$ffmpeg -framerate 8 -pattern_type glob -i './frames/*.png' -c:v libx264 -r 30 -pix_fmt yuv420p example.mp4
```

