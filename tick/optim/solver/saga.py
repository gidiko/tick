# License: BSD 3 clause

from tick.optim.model.base import ModelGeneralizedLinear
from tick.optim.solver.base import SolverFirstOrderSto
from tick.optim.solver.build.solver import SAGA as _SAGA

__author__ = "Stephane Gaiffas"

variance_reduction_methods_mapper = {
    'last': _SAGA.VarianceReductionMethod_Last,
    'avg': _SAGA.VarianceReductionMethod_Average,
    'rand': _SAGA.VarianceReductionMethod_Random
}


class SAGA(SolverFirstOrderSto):
    """Stochastic average gradient algorithm

    Parameters
    ----------
    epoch_size : `int`
        Epoch size

    rand_type : `str`
        Type of random sampling

        * if ``"unif"`` samples are uniformly drawn among all possibilities
        * if ``"perm"`` a random permutation of all possibilities is
          generated and samples are sequentially taken from it. Once all of
          them have been taken, a new random permutation is generated

    tol : `float`, default=0
        The tolerance of the solver (iterations stop when the stopping
        criterion is below it). By default the solver does ``max_iter``
        iterations

    max_iter : `int`
        Maximum number of iterations of the solver

    verbose : `bool`, default=True
        If `True`, we verbose things, otherwise the solver does not
        print anything (but records information in history anyway)

    print_every : `int`, default = 10
        Print history information every time the iteration number is a
        multiple of ``print_every``

    record_every : `int`, default = 1
        Information along iteration is recorded in history each time the
        iteration number of a multiple of ``record_every``

    variance_reduction : {'last', 'avg', 'rand'}, default = last
        Determine what is used as phase iterate for variance reduction.

        * 'last' : the phase iterate is the last iterate of the previous epoch
        * 'avg' : the phase iterate is the average over the iterates in the past
          epoch
        * 'rand': the phase iterate is a random iterate of the previous epoch

    Attributes
    ----------
    model : `Solver`
        The model to solve

    prox : `Prox`
        Proximal operator to solve

    References
    ----------
    A. Defazio, F. Bach, S. Lacoste-Julien, SAGA: A fast incremental gradient
    method with support for non-strongly convex composite objectives, NIPS 2014
    """

    def __init__(self, step: float = None, epoch_size: int = None,
                 rand_type: str = "unif", tol: float = 0.,
                 max_iter: int = 100, verbose: bool = True,
                 print_every: int = 10, record_every: int = 1,
                 seed: int = -1, variance_reduction: str = "last"):

        SolverFirstOrderSto.__init__(self, step, epoch_size, rand_type,
                                     tol, max_iter, verbose,
                                     print_every, record_every, seed=seed)
        step = self.step
        if step is None:
            step = 0.

        epoch_size = self.epoch_size
        if epoch_size is None:
            epoch_size = 0

        # Construct the wrapped C++ SAGA solver
        self._solver = _SAGA(epoch_size, self.tol,
                             self._rand_type, step, self.seed)

        self.variance_reduction = variance_reduction

    @property
    def variance_reduction(self):
        return next((k for k, v in variance_reduction_methods_mapper.items()
                     if v == self._solver.get_variance_reduction()), None)

    @variance_reduction.setter
    def variance_reduction(self, val: str):

        if val not in variance_reduction_methods_mapper:
            raise ValueError(
                'variance_reduction should be one of "{}", got "{}".'.format(
                    ', '.join(variance_reduction_methods_mapper.keys()),
                    val))

        self._solver.set_variance_reduction(
            variance_reduction_methods_mapper[val])

    def set_model(self, model: ModelGeneralizedLinear):
        """Set model in the solver

        Parameters
        ----------
        model : `ModelGeneralizedLinear`
            Sets the model in the solver. The model gives the first
            order information about the model (loss, gradient, among
            other things). SAGA only accepts childs of `ModelGeneralizedLinear`

        Returns
        -------
        output : `Solver`
            The `Solver` with given model
        """
        if isinstance(model, ModelGeneralizedLinear):
            return SolverFirstOrderSto.set_model(self, model)
        else:
            raise ValueError("SAGA accepts only childs of "
                             "`ModelGeneralizedLinear`")