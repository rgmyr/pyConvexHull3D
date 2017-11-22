from pydcel import dcel

def colinear(p1, p2, p3):
    return (cross(p2-p1, p3-p2) == 0)



class ConvexHull3D():
    '''
    Convex Hull of 3D point set using randomized incremental method from de Berg.
    
    pts: array-like with shape [n_points, 3]

    '''
    def __init__(self, pts=None):
        assert len(pts) > 3
        self.pts = pts
        self.dcel = dcel.DCEL()

    def encloses(self, new_pt):
        '''Return True if new_pt is inside current hull, else False'''
        pass

    def visible_faces(self, new_pt):
        '''Return list(dict?) of visibility of each face from new_pt'''
        

    def add_pt(self, new_pt)


        pass
    

    def run_algorithm(self):
        pass




            

