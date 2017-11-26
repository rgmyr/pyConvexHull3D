from hull3D import ConvexHull3D
from scipy import spatial
import numpy as np


def main():
    # integer coords in small box
    print("FIVE TESTS: 100 integer points in [-10,10]^3 box")
    for i in range(5):
        print("\nTEST {}:".format(i+1))
        pts = np.random.randint(-10, 10, (100, 3))

        myHull = ConvexHull3D(pts)
        mine = set(myHull.getVertexIndices())
        print("\t This : {}".format(len(mine)))

        scipyHull = spatial.ConvexHull(myHull.getPts())
        qhull = set(scipyHull.vertices)
        print("\t QHull: {}".format(len(qhull)))

        if mine == qhull:
            print("\t\t *EQUIVALENT*")
        elif mine.issuperset(qhull):
            print("\t\t *This.isSUPERSET(Qhull)*")
        else:
            print("\t\t  *****ERROR*****")

    # integer coords in a big box        
    print("\n\nFIVE TESTS: 100 integer points in [-100,100]^3 box")
    for i in range(5):
        print("\nTEST {}:".format(i+1))
        pts = np.random.randint(-100, 100, (100, 3))

        myHull = ConvexHull3D(pts)
        mine = set(myHull.getVertexIndices())
        print("\t This : {}".format(len(mine)))

        scipyHull = spatial.ConvexHull(myHull.getPts())
        qhull = set(scipyHull.vertices)
        print("\t QHull: {}".format(len(qhull)))

        if mine == qhull:
            print("\t\t *EQUIVALENT*")
        elif mine.issuperset(qhull):
            print("\t\t *This.isSUPERSET(Qhull)*")
        else:
            print("\t\t  *****ERROR*****")

    # float coords in whatever box
    print("\n\nFIVE TESTS: 100 float points in a [-1,1]^3 box")
    for i in range(5):
        print("\nTEST {}:".format(i+1))
        pts = np.random.uniform(low=-1.0, high=1.0, size=(100, 3))

        myHull = ConvexHull3D(pts)
        mine = set(myHull.getVertexIndices())
        print("\t This : {}".format(len(mine)))

        scipyHull = spatial.ConvexHull(myHull.getPts())
        qhull = set(scipyHull.vertices)
        print("\t QHull: {}".format(len(qhull)))

        if mine == qhull:
            print("\t\t *EQUIVALENT*")
        elif mine.issuperset(qhull):
            print("\t\t *This.isSUPERSET(Qhull)*")
        else:
            print("\t\t  *****ERROR*****")


if __name__ == "__main__":
    main()
