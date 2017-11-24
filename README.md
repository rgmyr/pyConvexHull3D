# pyConvexHull3D

`dcel.py`: Provides the doubly-connected edge list, Vertex, hEdge, and Face classes. `DCEL` is a `dict`-based implementation, adapted from the `list`-based python 2.7 implementation at: [https://github.com/Ylannl/pydcel](https://github.com/Ylannl/pydcel). Python version >=3.6 is strongly recommended, as the implementation here assumes that dictionaries preserve insertion order.

`hull3D.py`: Provides the `ConvexHull3D` algorithm class with visualization capabilities.

`test.py`: Runs tests and prints output.

## Dependencies  

Aside from standard library modules `collections` and `itertools`, running the algorithm requires `numpy` and `matplotlib`. Running `test.py` requires `scipy`, as the solutions are tested against those produced by `scipy.spatial.ConvexHull()` (which calls the `QHull` library). 

## Future Updates

Currently `pyConvexHull3D` produces the exact solution for sets of points in general position (in the sense of no three points on the hull being colinear). This is almost always the case when using float coordinates, or integer coordinates in a bounding cube that is large relative to the number of points. When there are colinear points on the hull, the vertices reported by `QHull` are a proper subset of those reported by `pyConvexHull3D`.

## Usage
```Python
from hull3D import ConvexHull3d
import numpy as np

pts = np.random.randint(-100, 100, (100,3))

Hull = ConvexHull3D(pts, run=True, preproc=True, make_frames=False, frames_dir='./frames/')

# To get vertex objects:
vertices = Hull.DCEL.vertexDict.values()

# To get indices:
pts = Hull.getPts()    # if preproc=True
hull_vertices = pts[Hull.getVertexIndices()]
```

- pts

:np.array with shape `(n, 3)`

- preproc=True      

: set False to disable preprocessing

run=True          : set False to run algorithm only when self.runAlgorithm() is called

make_frames=False : set True to output png frames at each step to frame_dir

frames_dir='./frames/' : set to change dir where frames are saved

Use hull.generateImage(show=True) to use plt.show() rather than saving png. If make_frames=False, it will use plt.show() by default.

        To get (current) hull vertices, use self.DCEL.vertexDict.values() --> Vertex objects
                or, self.getVertexIndices() --> indices relative to pts or preprocess(pts)

        If you want to compare output with preprocess(pts) call self.getPts()





The example `mp4` movie for 100 randomly distributed points was produced with `ffmpeg`:
```
$ffmpeg -framerate 8 -pattern_type glob -i './frames/*.png' -c:v libx264 -r 30 -pix_fmt yuv420p example.mp4
```

