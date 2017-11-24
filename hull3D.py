from dcel import DCEL, Vertex
from numpy import array, unique, append, dot, cross
from collections import deque
from itertools import permutations
from random import sample

import mpl_toolkits.mplot3d as mpl3D
import matplotlib.pyplot as plt


def colinear(p0, p1, p2):
    return all(cross(p1-p0, p2-p1) == 0)

def coplanar(p1, p2, p3, p0):
    return dot(cross(p1-p0, p2-p1), p0-p3) == 0

def preprocess(pts):
    """Assumes pts is an np.array with shape (n, 3).
       Removes duplicate points.
       Swaps (unique) rows to front like [xmax, xmin, ymax, ymin, zmax, zmin]  
    """
    pts = unique(pts, axis=0)
    pts = array(sample(list(pts), len(pts)))
    pts[[0, pts[:,0].argmax()]]  = pts[[pts[:,0].argmax(), 0]]
    pts[[1, pts[1:,0].argmin()+1]] = pts[[pts[1:,0].argmin()+1, 1]]
    pts[[2, pts[2:,1].argmax()+2]] = pts[[pts[2:,1].argmax()+2, 2]]
    pts[[3, pts[3:,1].argmin()+3]] = pts[[pts[3:,1].argmin()+3, 3]]
    if len(pts) > 4:
        pts[[4, pts[4:,2].argmax()+4]] = pts[[pts[4:,2].argmax()+4, 4]]
    if len(pts) > 5:
        pts[[5, pts[5:,2].argmin()+5]] = pts[[pts[5:,2].argmin()+5, 5]]
    return pts


class ConvexHull3D():
    '''
    Convex Hull of 3D point based on randomized incremental method from de Berg.
    
    Input: pts [np.array with shape (n_points, 3)]. Points should be unique.

    Params: preproc=True      : set False to disable preprocessing
            run=True          : set False to run algorithm only when self.runAlgorithm() is called
            make_frames=False : set True to output png frames at each step to frame_dir
            frames_dir='./frames/' : set to change dir where frames are saved
    '''
    def __init__(self, pts, run=True, preproc=False, make_frames=False, frames_dir='./frames/'):
        """Creates initial 4-vertex polyhedron."""
        assert pts.shape[1] == 3
        assert len(pts) > 3

        self.make_frames = make_frames
        if make_frames: 
            self.pad = len(str(2*len(pts)))
            self.frames_dir = frames_dir
            self.frames_count = 0

        if preproc:
            self.pts = preprocess(pts)
        else:
            self.pts = unique(pts, axis=0)
            # random array gets sorted by unique
            self.pts = array(sample(list(self.pts), len(self.pts)))

        self.boxmax, self.boxmin = pts.max(), pts.min()

        self.id_to_idx = {}
        self.DCEL = DCEL()
        self.removeVertexSet = set()
        self.removeHEdgeSet  = set()
        self.removeFaceSet   = set()
        self.safeVertexSet   = set()
        self.safeHEdgeSet    = set()

        # create first vertices and define CCW (outward normal) order
        v0, v1, v2, v3 = tuple(self.DCEL.createVertex(*self.pts[i]) for i in range(4))
        self.id_to_idx[3] = 3
        AB = dot(cross(v1-v0, v2-v1), v0-v3)  
        if AB == 0:
            error = ("First 4 pts are coplanar. Try passing preproc=False and using "+
                     "np.random.shuffle(pts). If error persists, pts may all be coplanar.")
            raise ValueError(error)
        elif AB < 0:
            vertices = (v0, v1, v2)
        else:
            vertices = (v0, v2, v1)

        # first triangle face and all edges + twins
        face = self.DCEL.createFace()
        hedges = [self.DCEL.createHedge() for _ in range(6)]
        for h, v in zip(hedges[:3], vertices):
            self.id_to_idx[v.identifier] = v.identifier
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

        if self.make_frames: self.generateImage()
        self.updateHull(v3, hedges[3:])
        if self.make_frames: self.generateImage()

        if run:
            self.runAlgorithm()

    def getPts(self):
        return self.pts

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
            if dot(face.normal, face.edgeComponent.origin-newV) > 0:
                visibility[face.identifier] = True
                # add all visible components to the removeSets
                self.removeFaceSet.add(face)
                for h in face.edgeComponent.loop():
                    self.removeHEdgeSet.add(h)
                for v in face.loopOuterVertices():
                    self.removeVertexSet.add(v)
            else:
                visibility[face.identifier] = False
            '''
            if dot(face.normal, face.edgeComponent.origin-newV) == 0:
                print(newV, " was coplanar with a face")
            '''

        return visibility

    def getBoundaryChain(self, visibility):
        """visibility should be dict from self.getVisibilityDict(newPt)."""
        # find first hedge in chain
        boundary = []
        for identifier, visible in visibility.items():
            if visible:
                # check if any hedges have twin.incidentface = not visible
                for h in self.DCEL.faceDict[identifier].edgeComponent.loop():
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
        """Generate components, set topologies, delete superceded components."""
        # loop over single new triangles
        for h in boundary:
            f = self.DCEL.createFace()
            _h, h_ = tuple(self.DCEL.createHedge() for _ in range(2))
            for hedge in [_h, h, h_]:
                hedge.incidentFace = f
            _h.origin, h_.origin = v_new, h.next.origin
            _h.previous, h.previous, h_.previous = h_, _h, h
            _h.next, h.next, h_.next = h, h_, _h
            f.setTopology(h)

        v_new.incidentEdge = boundary[0].previous

        # now set the twins
        for i in range(-1,len(boundary)-1):
            """ NOTE: Colinear case sames to be related to extra vertices
            if colinear(v_new, h.origin, h.twin.previous.origin):
                print("COLINEAR!")
            """
            boundary[i].next.twin = boundary[i+1].previous 
            boundary[i+1].previous.twin = boundary[i].next

        self.removeConflicts()
        return

    def insertPoint(self, newPt, i):
        """Update the hull given new point."""
        if self.make_frames: self.generateImage(newPt=newPt)
        visibility = self.getVisibilityDict(newPt)
        if not any(list(visibility.values())):
            return

        boundary = self.getBoundaryChain(visibility)
        v_new = self.DCEL.createVertex(*newPt)
        self.id_to_idx[v_new.identifier] = i+4
        self.updateHull(v_new, boundary) 
        if self.make_frames: self.generateImage()
        return 

    def runAlgorithm(self, make_frames=False):
        for i, pt in enumerate(self.pts[4:]):
            self.insertPoint(pt, i)
        return

    def getVertexIndices(self):
        return list(self.id_to_idx[identifier] for identifier in self.DCEL.vertexDict.keys())

    def generateImage(self, newPt=None, show=False):
        """Plot all the faces and vertices on a 3D axis"""
        ax = mpl3D.Axes3D(plt.figure(figsize=[20,15]))
        ax.set_xlim([self.boxmin,self.boxmax])
        ax.set_ylim([self.boxmin,self.boxmax])
        ax.set_zlim([self.boxmin,self.boxmax])

        vertices = array([list(v.p()) for v in self.DCEL.vertexDict.values()])
        if newPt is not None: vertices = append(vertices, array([newPt]), axis=0)
        ax.scatter(vertices[:,0], vertices[:,1], vertices[:,2], s=50, c='r', marker='o')

        alpha = 0.1
        for face in self.DCEL.faceDict.values():
            tri = mpl3D.art3d.Poly3DCollection([[list(v.p()) for v in face.loopOuterVertices()]])
            tri.set_facecolor((0,0,1, 0.2)) # add functionality for visible faces later
            #tri.set_alpha(0.1)
            tri.set_edgecolor((0,0,0, 0.2))
            ax.add_collection3d(tri)
       
        if show or not self.make_frames: 
            plt.show()
        else:
            plt.savefig(self.frames_dir+'frame_'+str(self.frames_count).zfill(self.pad))
            plt.close()
            self.frames_count += 1
