from dcel import DCEL, Vertex
from numpy import dot, cross
from collections import deque
from itertools import permutations
import scipy as sp

import mpl_toolkits.mplot3d as mpl3D
import matplotlib.colors as colors
import matplotlib.pyplot as plt


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

        self.pts = pts
        self.DCEL = DCEL()
        self.removeVertexSet = set()
        self.removeHEdgeSet  = set()
        self.removeFaceSet   = set()
        self.safeVertexSet   = set()
        self.safeHEdgeSet    = set()

        # create first vertices and define CCW (outward normal) order
        v0, v1, v2, v3 = tuple(self.DCEL.createVertex(*pts[i]) for i in range(4))
        if dot(cross(v1-v0, v2-v1), v0-v3) < 0:
            vertices = (v0, v1, v2)
        else:
            vertices = (v0, v2, v1)

        # first triangle face and all edges + twins
        face = self.DCEL.createFace()
        hedges = [self.DCEL.createHedge() for _ in range(6)]
        for h, v in zip(hedges[:3], vertices):
            h.incidentFace = face
            v.incidentEdge = h
        for h, _h, v in zip(hedges, hedges[::-1], sum(permutations(vertices, 3), ())):
            h.origin = v
            h.twin = _h

        deqA, deqB = deque(hedges[:3]), deque(hedges[3:])
        for _ in range(3):
            for deq in [deqA, deqB]:
                h, h_, _h = tuple(deq)
                h.next, h.previous = h_, _h
                deq.rotate(1)

        face.setTopology(hedges[0])

        self.generateImage()
        # second three hedges form visible boundary chain for v4
        self.updateHull(v3, hedges[3:])
        self.generateImage()

    def removeConflicts(self):
        """Remove all visible elements that were not on boundary."""
        for f in self.removeFaceSet:
            self.DCEL.remove(f)
        for v in self.removeVertexSet.difference(self.safeVertexSet):
            self.DCEL.remove(v)
        for h in self.removeHEdgeSet.difference(self.safeHEdgeSet):
            self.DCEL.remove(h)
        
        self.removeVertexSet = set()
        self.removeHEdgeSet  = set()
        self.removeFaceSet   = set()
        self.safeVertexSet   = set()
        self.safeHEdgeSet    = set()

    def getVisibilityDict(self, newPt):
        """Returns dict of {face.id: bool is_visible_from_newPt}."""
        visibility = {}
        newV = Vertex(*newPt)
        # For now we consider the coplanar case to be not visible
        for face in self.DCEL.faceDict.values():
            if dot(face.normal, face.outerComponent.origin-newV) > 0:
                visibility[face.identifier] = True
                # add all visible components to the removeSets
                self.removeFaceSet.add(face)
                for h in face.outerComponent.loop():
                    self.removeHEdgeSet.add(h)
                for v in face.loopOuterVertices():
                    self.removeVertexSet.add(v)
            else:
                visibility[face.identifier] = False

        print("faceDict:\n", self.DCEL.faceDict.keys())
        print("visibility:\n", visibility.keys())

        return visibility

    def getBoundaryChain(self, visibility):
        """visibility should be dict from self.getConflictDict(newPt)"""
        # find first hedge in chain
        boundary = []
        for identifier, visible in visibility.items():
            if visible:
                # check if any hedges have twin.incidentface = not visible
                for h in self.DCEL.faceDict[identifier].outerComponent.loop():
                    if not visibility[h.twin.incidentFace.identifier]:
                        boundary.append(h)
                        self.safeHEdgeSet.add(h)
                        self.safeVertexSet.add(h.origin)
                        break
            if len(boundary) != 0:
                break

        # find boundary hedges, updating safeSets
        while boundary[-1].next.origin != boundary[0].origin:
            for h in boundary[-1].next.wind():
                hVis = visibility[h.incidentFace.identifier] 
                hTwinVis =  visibility[h.twin.incidentFace.identifier]
                if hVis and not hTwinVis:
                    self.safeHEdgeSet.add(h)
                    self.safeVertexSet.add(h.origin)
                    boundary.append(h)
                    break
                    
        return boundary

    def updateHull(self, v_new, boundary):
        """Generate components & set topologies given newPt and boundary chain."""
        # loop over single new triangles
        for h in boundary:
            f = self.DCEL.createFace()
            _h, h_ = tuple(self.DCEL.createHedge() for _ in range(2))
            v_new.incidentEdge = _h
            for hedge in [_h, h, h_]:
                hedge.incidentFace = f
            _h.origin, h_.origin = v_new, h.next.origin
            _h.previous, h.previous, h_.previous = h_, _h, h
            _h.next, h.next, h_.next = h, h_, _h
            f.setTopology(h)

        # now set the twins
        boundary[-1].next.twin = boundary[0].previous
        boundary[0].previous.twin = boundary[-1].next
        for i in range(len(boundary)-1):
            boundary[i].next.twin = boundary[i+1].previous 
            boundary[i+1].previous.twin = boundary[i].next

        self.removeConflicts()
        return

    def insertPoint(self, newPt):
        """Update the hull given new point."""
        visibility = self.getVisibilityDict(newPt)
        if not any(list(visibility.values())):
            return
        
        # TODO: make red/blue coded plot
        #if self.make_frames == True:

        boundary = self.getBoundaryChain(visibility)
        v_new = self.DCEL.createVertex(*newPt)
        self.updateHull(v_new, boundary) 
        return

    def runAlgorithm(self, make_frames=False):
        for pt in self.pts[4:]:
            self.insertPoint(pt)
            if make_frames:
                self.generateImage()
        return

    def generateImage(self):
        """Plot all the faces on a 3D axis"""
        ax = mpl3D.Axes3D(plt.figure(figsize=[20,15]))
        ax.set_xlim([-10,10])
        ax.set_ylim([-10,10])
        ax.set_zlim([-10,10])

        for face in self.DCEL.faceDict.values():
            tri = mpl3D.art3d.Poly3DCollection([[list(v.p()) for v in face.loopOuterVertices()]])
            tri.set_color(colors.rgb2hex(sp.rand(3))) # add functionality for visible faces later
            tri.set_alpha(0.1)
            tri.set_edgecolor('k')
            ax.add_collection3d(tri)

        ax.set_alpha(0.2)
        ax.scatter(self.pts[:,0], self.pts[:,1], self.pts[:,2], c='r', marker='o')

        plt.show()

        




            

