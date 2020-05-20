import numpy as np

from .GaussLobattoQuadrature import GaussLobattoQuadrature
from .GaussLegendreQuadrature import GaussLegendreQuadrature

class FEMeshIntegralAlg():
    def __init__(self, mesh, q, cellmeasure=None):
        self.mesh = mesh
        self.integrator = mesh.integrator(q)
        self.cellmeasure = cellmeasure if cellmeasure is not None \
                else mesh.entity_measure('cell')

        self.edgemeasure = mesh.entity_measure('edge')
        self.edgebarycenter = mesh.entity_barycenter('edge')
        self.edgeintegrator = GaussLegendreQuadrature(q)


    def integral(self, u, celltype=False, barycenter=True):
        qf = self.integrator
        bcs = qf.quadpts # 积分点 (NQ, 3)
        ws = qf.weights # 积分点对应的权重 (NQ, )
        if barycenter:
            val = u(bcs)
        else:
            ps = self.mesh.bc_to_point(bcs) # (NQ, NC, 2)
            val = u(ps)
        dim = len(ws.shape)
        s0 = 'abcde'
        s1 = '{}, {}j..., j->j...'.format(s0[0:dim], s0[0:dim])
        e = np.einsum(s1, ws, val, self.cellmeasure)
        if celltype is True:
            return e
        else:
            return e.sum()

    def L2_norm(self, uh, celltype=False):
        def f(x):
            return uh(x)**2

        e = self.integral(f, celltype=celltype)
        if celltype is False:
            return np.sqrt(e.sum())
        else:
            return np.sqrt(e)

    def L2_norm_1(self, uh, celltype=False):
        def f(x):
            return np.sum(uh**2, axis=-1)*self.cellmeasure

        e = self.integral(f, celltype=celltype)
        if celltype is False:
            return np.sqrt(e.sum())
        else:
            return np.sqrt(e)

    def L1_error(self, u, uh, celltype=False):
        def f(x):
            xx = self.mesh.bc_to_point(x)
            return np.abs(u(xx) - uh(x))
        e = self.integral(f, celltype=celltype)
        if celltype is False:
            return e.sum()
        else:
            return e
        return

    def L2_error(self, u, uh, celltype=False):
        def f(bc):
            xx = self.mesh.bc_to_point(bc)
            return (u(xx) - uh(bc))**2
        e = self.integral(f, celltype=celltype)
        if celltype is False:
            return np.sqrt(e.sum())
        else:
            return np.sqrt(e)
        return 

    def L2_error_uI_uh(self, uI, uh, celltype=False):
        def f(x):
            return (uI(x) - uh(x))**2
        e = self.integral(f, celltype=celltype)
        if celltype is False:
            return np.sqrt(e.sum())
        else:
            return np.sqrt(e)
        return 

    def Lp_error(self, u, uh, p, celltype=False):
        def f(x):
            xx = self.mesh.bc_to_point(x)
            return np.abs(u(xx) - uh(x))**p
        e = self.integral(f, celltype=celltype)
        if celltype is False:
            return e.sum()**(1/p)
        else:
            return e**(1/p)
        return 
