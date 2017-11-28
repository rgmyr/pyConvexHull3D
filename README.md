# pyConvexHull3D

`dcel.py`: Provides the doubly-connected edge list, Vertex, hEdge, and Face classes. `DCEL` is a `dict`-based implementation, adapted from the `list`-based python2 implementation at [Ylannl/pydcel](https://github.com/Ylannl/pydcel). Python version >=3.6 is strongly recommended, as this implementation assumes that dictionaries preserve insertion order. In theory, it should work with `collections.OrderedDict` as well, but this has not been tested. I chose not use `OrderedDict` here because it is a pure Python structure and as a result is much slower.

`hull3D.py`: Provides the `ConvexHull3D` algorithm class with visualization capabilities.

`test.py`: Runs tests: compares `ConvexHull3d` output to `QHull` output and prints results.

## Dependencies  

Aside from standard library modules `collections` and `itertools`, running the algorithm requires `numpy` and `matplotlib`. Running `test.py` requires `scipy`, as the solutions are tested against those produced by `scipy.spatial.ConvexHull()` (which calls the `QHull` library). 

## Future Updates

Currently `pyConvexHull3D` produces the exact solution for sets of points in general position (in the restricted sense of no three points on hull boundary being colinear, and no four adjacent points on the hull boundary being coplanar). This is almost always the case when using float coordinates, or when using random integer coordinates with a bounding box that is large relative to the number of points. When there *are* such points on the hull, the vertices reported by `QHull` are a proper subset of those reported by `pyConvexHull3D`.

## Usage

Simple usage example:
```Python
from hull3D import ConvexHull3D
import numpy as np

pts = np.random.randint(-100, 100, (100,3))

# Showing default parameters
Hull = ConvexHull3D(pts, run=True, preproc=False, make_frames=False, frames_dir='./frames/')

# To get Vertex objects:
vertices = Hull.DCEL.vertexDict.values()

# To get indices:
pts = Hull.getPts()    # to get pts in order used by ConvexHull3d
hull_vertices = pts[Hull.getVertexIndices()]

# To get vertices of each Face:
faces = [[list(v.p()) for v in face.loopOuterVertices()] for face in Hull.faceDict.values()]
```

#### Parameter explanations:

`pts`
- Should be type np.array with shape `(n, 3)`. **NOTE**: duplicate points will be removed.

`run=True`         
- Set to `False` to run full algorithm at a later time by calling `Hull.runAlgorithm()`.

`preproc=False`
- Set to `True` to use preprocessing function, which swaps rows in `pts` such that Hull(`i=6`) is more likely to be large.

`make_frames=False`
- Set to `True` to output png frames at each step to `frame_dir`.

`frames_dir='./frames/'`
- Set to change directory where frames are saved if `make_frames=True`. This directory should exist.

#### Other Usage

Call `Hull.generateImage(show=True)` to generate and output an image using `plt.show()` rather than saving a png file. If `make_frames=False`, then this method will use `plt.show()` by default.

If `preproc=True` and you want to compare output with another algorithm, call `Hull.getPts()` to get the points in the preprocessed order used by `Hull`. This is good practice anyway, unless you are certain that `pts` are unique.

The included `example.mp4` movie for 100 randomly distributed integer points was produced with `ffmpeg`:
```
$ffmpeg -framerate 8 -pattern_type glob -i './frames/*.png' -c:v libx264 -r 30 -pix_fmt yuv420p example.mp4
```

