# pyConvexHull3D

`dcel.py`: Provides the doubly-connected edge list, Vertex, hEdge, and Face classes. `DCEL` is a `dict`-based implementation, adapted from the `list`-based python 2.7 implementation at: [https://github.com/Ylannl/pydcel](https://github.com/Ylannl/pydcel). Python version >=3.6 is strongly recommended, as the implementation here assumes that dictionaries preserve insertion order.

`hull3D.py`: Provides the `ConvexHull3D` algorithm class with visualization capabilities.

`test.py`: Runs tests and prints output.

## Dependencies  

Aside from standard library modules `collections` and `itertools`, running the algorithm requires `numpy` and `matplotlib`. Running `test.py` requires `scipy`, as the solutions are tested against those produced by `scipy.spatial.ConvexHull()` (which calls the `QHull` library). 

## Future Updates

Currently the `pyConvexHull3D` produces the exact solution for sets of points in general position (in the sense of no three points on the hull being colinear). This is almost always the case when using float coordinates, or integer coordinates in a bounding cube that is large relative to the number of points. When there are colinear points on the hull, the vertices reported by `QHull` are a proper subset of those reported by `pyConvexHull3D`.

## Usage




The example `mp4` movie was produced with `ffmpeg`:

```
$ffmpeg -framerate 8 -pattern_type glob -i './frames/*.png' -c:v libx264 -r 30 -pix_fmt yuv420p example.mp4
```

