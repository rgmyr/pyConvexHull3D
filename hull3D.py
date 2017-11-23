from dcel import DCEL
from numpy import dot, cross
from collections import deque
from itertools import permutations


def colinear(p0, p1, p2):
    return all(cross(p1-p0, p2-p1) == 0)

def coplanar(p1, p2, p3, p0):
    return dot(cross(p1-p0, p2-p1), p0-p3) == 0


class ConvexHull3D():
    '''
    Convex Hull of 3D point based on randomized incremental method from de Berg.
    
    Input: pts [array-like with shape (n_points, 3)]

    '''
    def __init__(self, pts=None):
        """Creates initial 4-vertex polyhedron.
        TODO: - check for colinear/coplanar initial pts 
              - preprocess by moving maximal pts to the front?

        """
        assert pts.shape[1] == 3
        assert len(pts) > 3
        self.DCEL = DCEL()

        self.pts = pts

        # create vertices and define CCW (outward normal) order
        v0, v1, v2, v3 = tuple(self.DCEL.createVertex(*pts[i]) for i in range(4))
        if dot(cross(v1-v0, v2-v1), v0-v3) < 0:
            vertices = (v0, v1, v2)
        else:
            vertices = (v0, v2, v1)

        # first triangle face and all edges + twins
        face = self.DCEL.createFace()
        hedges = [self.DCEL.createHedge() for _ in range(6)]

        # first three hedges belong to first face
        for h, v in zip(hedges[:3], vertices):
            h.incidentFace = face
            v.incidentEdge = h

        # set hedge origins and twins
        for h, _h, v in zip(hedges, hedges[::-1], sum(permutations(vertices, 3), ())):
            h.origin = v
            h.twin = _h

        # set hedge next and previous
        deqA, deqB = deque(hedges[:3]), deque(hedges[3:])
        for _ in range(3):
            for deq in [deqA, deqB]:
                h, h_, _h = tuple(deq)
                h.next, h.previous = h_, _h
                deq.rotate(1)

        # now we can set face topo + normal
        face.setTopology(hedges[0])
        print("Face normal: ", face.normal)

        # second three hedges induce new triangles with v4
        #for h in hedges[3:]:
            #self.insertVertexWithChain()

        print(self.DCEL, "\n")
        print(self.getConflictDict(v3))


    def encloses(self, new_pt):
        '''Return True if new_pt is inside current hull, else False'''
        pass

    def removeWholeFace(self, face):
        '''Remove face and all of its hedges + vertices'''
        pass

    def removeBoundaryFace(self, face, hedge):
        '''Remove face and all components that are not on visibility boundary'''
        pass

    def getConflictDict(self, new_pt):
        '''Return list(dict?) of visibility of each face from new_pt'''
        visible = {}
        # For now we consider the coplanar case to be not visible
        for face in self.DCEL.faceDict.values():
            if dot(face.normal, face.outerComponent.origin-new_pt) > 0:
                visible[face.identifier] = True
            else:
                visible[face.identifier] = False

        return visible


    def insertVertexWithChain(self, new_v, h_chain):
        pass

    def runAlgorithm(self):
        pass




            

