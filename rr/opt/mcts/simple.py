from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import logging
import logging.config
import random
import time
from math import log, sqrt


__version__ = "0.3.0"
__author__ = "Rui Rei"
__copyright__ = "Copyright 2016-2017 {author}".format(author=__author__)
__license__ = "MIT"


INF = float("inf")
logger = logging.getLogger(__name__)
debug = logger.debug
info = logger.info
warn = logger.warning


def run(root, time_limit=INF, iter_limit=INF, pruning=None,
        rng_seed=None, rng_state=None, log_iter_interval=1000, sols=None):
    """
    Monte Carlo Tree Search for **minimization** problems.

    Note:
        Objective functions (and bounds) for maximization problems must be multiplied by -1.

    Arguments:
        root (TreeNode): the root of the search tree.
        time_limit (float): maximum CPU time allowed.
        iter_limit (int): maximum number of iterations.
        pruning (bool or None): make the search use/not use pruning if true/false. If `None` is
            given (default), auto-detects pruning settings from root node.
        rng_seed: an object to pass to `random.seed()`. Does not seed the RNG if no value is given.
        rng_state: an RNG state tuple, as obtained from `random.getstate()`. Can be used to set a
            particular RNG state at the start of the search.
        log_iter_interval (int): interval, in number of iterations, between automatic log messages.
        sols (Solutions): a Solutions object obtained from a previous run of MCTS. If this argument
            is provided, a previous search can be resumed from the point where it stopped.

    Returns:
        `Solutions` object containing the best solution found by the search, as well as the list
        of incumbent solutions during the search.
    """
    if pruning is None:
        # Guess pruning by comparing the bound() method from the root node's class with the
        # bound() method from the base TreeNode class.
        pruning = type(root).bound != TreeNode.bound
    if rng_seed is not None:
        info("Seeding RNG with {}...".format(rng_seed))
        random.seed(rng_seed)
    if rng_state is not None:
        rng_state_repr = "\n\t".join(map(str, rng_state))
        info("Setting RNG state to...\n\t{}".format(rng_state_repr))
        random.setstate(rng_state)
    info("Pruning is {}.".format("enabled" if pruning else "disabled"))

    t0 = time.process_time()  # initial cpu time
    if sols is None:
        info("Starting new search")
        sols = Solutions()  # object used to keep track of our best/worst solutions
        sol = root.simulate()  # run simulation from root and
        root.backpropagate(sol)  # backpropagate the solution
        sols.update(sol)
    else:
        info("Resuming previous search")
    t = time.process_time() - t0  # cpu time elapsed
    i = 0  # iteration count

    try:
        while i < iter_limit and t < time_limit:
            logger.log(
                level=logging.INFO if i % log_iter_interval == 0 else logging.DEBUG,
                msg="[i={:<5} t={:3.02f}] {}".format(i, t, sols),
            )
            node = root.select(sols)  # selection step
            # 
            if sols.best.value == 0:
                info("Search complete, solution is feasible")
                sols.best.is_opt = True
                break  # solution found
            #
            if node is None:
                info("Search complete, solution is optimal")
                sols.best.is_opt = True
                break  # tree exhausted
            new_children = node.expand(pruning=pruning, cutoff=sols.best.value)  # expansion step
            if len(new_children) == 0 and node.is_exhausted:
                node.delete()
            else:
                z0 = sols.best.value
                for child in new_children:
                    sol = child.simulate()  # simulation step
                    child.backpropagate(sol)  # backpropagation step
                    sols.update(sol)
                    assert child.sim_count > 0
                # prune only once after all child solutions have been accounted for
                if pruning and sols.best.value < z0:
                    ts0 = root.tree_size()
                    root.prune(sols.best.value)
                    ts1 = root.tree_size()
                    info("Pruning removed {} nodes ({} => {})".format(ts0 - ts1, ts0, ts1))
            # update elapsed time and iteration counter
            t = time.process_time() - t0
            i += 1
    except KeyboardInterrupt:
        info("Keyboard interrupt!")
    info("Finished at iter {} ({:.02f}s): {}".format(i, t, sols))
    return sols


class Infeasible(object):
    """
    Infeasible objects can be compared with other objects (such as floats), but always compare as
    greater (*i.e.* worse in a minimization sense) than those objects. Among infeasible objects,
    they compare by value, meaning that they can be used to represent different degrees of
    infeasibility.

    To inform the MCTS framework that a solution is infeasible, set an :class:`Infeasible` object
    as the solution's ``value`` attribute, like so:

    .. code-block:: python

        class MyNode(mcts.TreeNode):
            # (...)

            def simulate(self):
                # (...)
                infeas = len(self.unassigned_vars)
                if infeas > 0:
                    return mcts.Solution(value=mcts.Infeasible(infeas))
                # (...)

            # (...)
    """
    def __init__(self, infeas=+INF):
        self.infeas = infeas

    def __str__(self):
        return "{}({})".format(type(self).__name__, self.infeas)

    def __repr__(self):
        return "<{} @{:x}>".format(self, id(self))

    def __eq__(self, obj):
        return isinstance(obj, Infeasible) and self.infeas == obj.infeas

    def __ne__(self, obj):
        return not isinstance(obj, Infeasible) or self.infeas != obj.infeas

    def __gt__(self, obj):
        return not isinstance(obj, Infeasible) or self.infeas > obj.infeas

    def __ge__(self, obj):
        return not isinstance(obj, Infeasible) or self.infeas >= obj.infeas

    def __lt__(self, obj):
        return isinstance(obj, Infeasible) and self.infeas < obj.infeas

    def __le__(self, obj):
        return isinstance(obj, Infeasible) and self.infeas <= obj.infeas


class Solution(object):
    """Base class for solution objects. The :meth:`simulate` method of :class:`TreeNode` objects
    should return a :class:`Solution` object. Solutions can have solution data attached, but this
    is optional. The solution's value, however, is required.
    """
    def __init__(self, value, data=None):
        assert value is not None
        self.value = value  # objective function value (may be an Infeasible object)
        self.data = data  # solution data
        self.is_infeas = isinstance(value, Infeasible)  # infeasible solution flag
        self.is_feas = not self.is_infeas  # feasible solution flag
        self.is_opt = False  # optimal solution flag ("manually" set by run())

    def __str__(self):
        return "{}(value={}{})".format(type(self).__name__, self.value, "*" if self.is_opt else "")

    def __repr__(self):
        return "<{} @{:x}>".format(self, id(self))


class Solutions(object):
    """Simple auxiliary object whose only responsibility is to keep track of best and worst
    feasible and infeasible solutions, the best overall solution, and also a list of increasingly
    better solutions found during the search.
    """
    # Initial values for attributes of Solutions object.
    INIT_FEAS_BEST = Solution(value=+INF, data="<initial best feas solution>")
    INIT_FEAS_WORST = Solution(value=-INF, data="<initial worst feas solution>")
    INIT_INFEAS_BEST = Solution(value=Infeasible(+INF), data="<initial best infeas solution>")
    INIT_INFEAS_WORST = Solution(value=Infeasible(-INF), data="<initial worst infeas solution>")

    def __init__(self, *sols):
        self.list = []  # Solution list (only keeps solutions that improve upper bound)
        self.best = self.INIT_INFEAS_BEST  # best overall solution
        self.feas_count = 0  # number of feasible solutions seen
        self.feas_best = self.INIT_FEAS_BEST  # best feasible solution
        self.feas_worst = self.INIT_FEAS_WORST  # worst feasible solution
        self.infeas_count = 0  # number of infeasible solutions seen
        self.infeas_best = self.INIT_INFEAS_BEST  # best (least) infeasible solution
        self.infeas_worst = self.INIT_INFEAS_WORST  # worst (most) infeasible solution
        for sol in sols:
            self.update(sol)

    def __str__(self):
        attrs = ["feas_best", "feas_worst", "infeas_best", "infeas_worst"]
        descr = "feas_pct={:.0f}/{:.0f}, ".format(self.feas_pct, self.infeas_pct)
        descr += ", ".join("{}={}".format(attr, getattr(self, attr).value) for attr in attrs)
        return "{}({})".format(type(self).__name__, descr)

    def __repr__(self):
        return "<{} @{:x}>".format(self, id(self))

    @property
    def feas_ratio(self):
        return self.feas_count / (self.feas_count + self.infeas_count)

    @property
    def feas_pct(self):
        return self.feas_ratio * 100.0

    @property
    def infeas_ratio(self):
        return 1.0 - self.feas_ratio

    @property
    def infeas_pct(self):
        return self.infeas_ratio * 100.0

    def update(self, sol):
        # Update best and worst feasible solutions
        if sol.is_feas:
            self.feas_count += 1
            if sol.value < self.feas_best.value:
                debug("New best feasible solution: {} -> {}".format(self.feas_best, sol))
                self.feas_best = sol
            if sol.value > self.feas_worst.value:
                debug("New worst feasible solution: {} -> {}".format(self.feas_worst, sol))
                self.feas_worst = sol
        # Update best and worst infeasible solutions
        else:
            self.infeas_count += 1
            if sol.value < self.infeas_best.value:
                debug("New best infeasible solution: {} -> {}".format(self.infeas_best, sol))
                self.infeas_best = sol
            if sol.value > self.infeas_worst.value:
                debug("New worst infeasible solution: {} -> {}".format(self.infeas_worst, sol))
                self.infeas_worst = sol
        # Update best overall solution
        if sol.value < self.best.value:
            info("New best solution: {} -> {}".format(self.best, sol))
            self.best = sol
            self.list.append(sol)


class TreeNodeExpansion(object):
    """Lazy generator of child nodes.

    This object creates a copy of a given parent node and applies the next (unexpanded) branch in
    its branch list on demand. When the parent node has been completely expanded, the 'next()'
    method will return None and the 'is_finished' flag is set to true.
    """
    def __init__(self, node):
        self.node = node
        self.branches = None
        self.next_branch = None
        self.is_started = False
        self.is_finished = False

    def start(self):
        if self.is_started:
            raise ValueError("multiple attempts to start node expansion")
        self.branches = iter(self.node.branches())
        self.is_started = True
        self._advance_branch()

    def next(self):
        if self.is_finished:
            raise ValueError("node expansion is already finished")
        child = self.node.copy()
        child.apply(self.next_branch)
        self._advance_branch()
        return child

    def _advance_branch(self):
        try:
            self.next_branch = next(self.branches)
        except StopIteration:
            self.next_branch = None
            self.is_finished = True


class TreeNode(object):
    """Base class for tree nodes. Subclasses should define:

    :tree management methods:
        - :meth:`root`
        - :meth:`copy`
        - :meth:`branches`
        - :meth:`apply`
    :MCTS-related methods:
        - :meth:`simulate`
    :branch-and-bound related methods:
        - :meth:`bound` *[optional]*
    """

    Expansion = TreeNodeExpansion

    @classmethod
    def root(cls, instance):
        """Given a problem instance, create the root node for the associated search tree.

        Normally this method should create an empty node using ``root = cls()`` and then proceed
        to add the attributes necessary to fully represent a node in the tree.

        Parameters:
            instance: an object representing an instance of a specific problem. For example, for
                the knapsack problem, an instance would contain a list of item weights, a list of
                item values, and the knapsack's capacity. This could be a 3-tuple, a namedtuple,
                or even an instance of a custom class. The internal structure of the instance
                object is not dictated by the framework.

        Returns:
            TreeNode: the root of the search tree for the argument instance.
        """
        raise NotImplementedError()

    def __init__(self):
        cls = type(self)
        self.path = ()  # path from root down to, but excluding, 'self' (i.e. top-down ancestors)
        self.parent = None  # reference to parent node
        self.children = None  # list of child nodes (when expanded)
        self.expansion = cls.Expansion(self)  # child node generator

        # self.stats = cls.Stats(self)  # node statistics
        self.sim_count = 0  # number of simulations in this subtree
        self.sim_sol = None  # solution of this node's own simulation
        self.sim_best = None  # best solution of simulations in this subtree

    @property
    def depth(self):
        """Depth of the node in the tree, *i.e.* the number of ancestors of the current node."""
        return len(self.path)

    @property
    def is_expanded(self):
        """True iff the node's expansion has finished."""
        return self.expansion.is_finished

    @property
    def is_exhausted(self):
        """True iff the node is fully expanded and all its children were removed from the tree."""
        return self.is_expanded and len(self.children) == 0

    def tree_size(self):
        stack = [self]
        count = 1
        while len(stack) > 0:
            node = stack.pop()
            children = node.children
            if children is not None:
                stack.extend(children)
                count += len(children)
        return count

    def add_child(self, node):
        node.path = self.path + (self,)
        node.parent = self
        self.children.append(node)

    def remove_child(self, node):
        node.path = ()
        node.parent = None
        self.children.remove(node)

    # Tree management abstract methods
    # --------------------------------
    def copy(self):
        """Create a new node representing a copy of the node's state.

        This method should create a new "blank" node using ``clone = TreeNode.copy(self)``,
        which takes care of copying generic MCTS node attributes, and should then fill in the
        domain-specific data by shallow- or deep-copying the custom attributes that were
        previously defined in :meth:`root`. Note that some attributes should be unique for each
        node (hence copied deeply), while others can (and should, if possible) be shared among
        all nodes. This should be analyzed on a case-by-case basis.

        Returns:
            TreeNode: a clone of the current node.
        """
        cls = type(self)
        clone = cls.__new__(cls)
        TreeNode.__init__(clone)
        return clone

    def branches(self):
        """Generate a collection of branch objects that are available from the current node.

        This method should produce a collection (*e.g* list, tuple, set, generator) of branch
        objects. A branch object is an object (of any type, and with any internal structure)
        which carries enough information to apply a modification (through :meth:`apply`) to a
        copy of the current node and obtain one of its child nodes. In some cases, a branch
        object may be something as simple as a boolean value (see *e.g.* the knapsack example).

        Returns:
            collection of branch objects.
        """
        raise NotImplementedError()

    def apply(self, branch):
        """Mutate the node's state by applying a branch (as produced by :meth:`branches`).

        The logic in this method is highly dependent on the internal structure of the nodes and
        branch objects that are returned by :meth:`branches`.

        Note:
            This method should operate in-place on the node. The :meth:`expand` method will take
            care of creating copies of the current node and calling :meth:`apply` on the copies,
            passing each branch object returned by :meth:`branches` and thereby generating the
            list of the current node's children.

        Parameters:
            branch: an object which should contain enough information to apply a local
                modification to (a copy of) the current node, such that the end result represents
                descending one level in the tree.
        """
        raise NotImplementedError()

    # This parameter controls interleaved selection of still-expanding parent nodes with their
    # children, thereby allowing the search to deepen without forcing the full expansion of all
    # ancestors. Turn off to force parents to be fully expanded before starting to select their
    # children.
    SELECTION_ALLOW_INTERLEAVING = True

    # MCTS-related methods
    def select(self, sols):
        """Pick the most favorable node for exploration.

        This method starts at the root and descends until a leaf is found. In each level the child
        to descend to is the one with the best selection score.
        """
        # Check if tree has been completely explored.
        if self.is_exhausted:
            return None
        # Go down the tree picking the best child at each step.
        curr_node = None
        next_node = self
        allow_interleaving = self.SELECTION_ALLOW_INTERLEAVING
        while next_node is not curr_node:
            curr_node = next_node
            curr_expansion = curr_node.expansion
            if not curr_expansion.is_started:
                break
            if curr_expansion.is_finished:
                cands = curr_node.children
            elif allow_interleaving:
                cands = itertools.chain(curr_node.children, [curr_node])
            else:
                break
            best_cands = max_elems(cands, key=lambda n: n.selection_score(sols))
            next_node = best_cands[0] if len(best_cands) == 1 else random.choice(best_cands)
        # TODO: remove the debug lines below
        #     if curr_expansion.is_finished:
        #         print(".", end="")
        #     elif next_node is curr_node:
        #         print("=", end="")
        #     else:
        #         print("!", end="")
        # print("  ", end="")
        # import sys
        # sys.stdout.flush()
        return curr_node

    def selection_score(self, sols):
        """Selection score uses an adapted UTC formula to balance exploration and exploitation.

        See https://en.wikipedia.org/wiki/Monte_Carlo_tree_search. The exploitation term has been
        adapted to the optimization context, where there is no concept of win ratio.
        """
        if self.sim_best.is_feas:
            z_node = self.sim_best.value
            z_best = sols.feas_best.value
            z_worst = sols.feas_worst.value
            min_exploit = sols.infeas_count / (sols.feas_count + sols.infeas_count)
            max_exploit = 1.0
        else:
            z_node = self.sim_best.value.infeas
            z_best = sols.infeas_best.value.infeas
            z_worst = sols.infeas_worst.value.infeas
            min_exploit = 0.0
            max_exploit = sols.infeas_count / (1 + sols.feas_count + sols.infeas_count)
        if z_best == z_worst:
            raw_exploit = 0.0
        else:
            raw_exploit = (z_worst - z_node) / (z_worst - z_best)
            assert 0.0 <= raw_exploit <= 1.0
        exploit = min_exploit + raw_exploit * (max_exploit - min_exploit)
        explore = (
            INF if self.parent is None else
            sqrt(2.0 * log(self.parent.sim_count) / self.sim_count)
        )
        expand = 1.0 / (1.0 + self.depth)
        return exploit + explore + expand

    # Parameter controlling how many child nodes (at most) are created during each iteration. The
    # default value is 1, which means that nodes are expanded one child at a time. This allows
    # the algorithm to pick other sites for exploration if the initial children of the current
    # node reveal it to be a bad choice.
    EXPANSION_LIMIT = 1

    def expand(self, pruning, cutoff):
        """Generate and link the children of this node.

        Note:
            The current implementation only creates at most 'EXPANSION_LIMIT' nodes.

        Returns:
            A list of newly created child nodes.
        """
        expansion = self.expansion
        if not expansion.is_started:
            assert self.children is None
            self.children = []
            expansion.start()
        new_children = []
        expansion_count = 0
        expansion_limit = self.EXPANSION_LIMIT
        while expansion_count < expansion_limit and not expansion.is_finished:
            child = expansion.next()
            if pruning and child.bound() >= cutoff:
                continue
            self.add_child(child)
            new_children.append(child)
            expansion_count += 1
        return new_children

    def simulate(self):
        """Run a simulation from the current node to completion or infeasibility.

        This method defines the simulation strategy that is used to obtain node value estimates
        in MCTS. It should quickly descend the tree until a leaf node (solution or infeasibility)
        is reached, and return the result encountered.

        Smarter simulation strategies incorporate more domain-specific knowledge and normally use
        more computational resources, but can dramatically improve the performance of the
        algorithm. However, if the computational cost is too high, MCTS may be unable to gather
        enough data to improve the accuracy of its node value estimates, and will therefore end
        up wasting time in uninteresting regions. For best results, a balance between these
        conflicting goals must be reached.

        Returns:
            Solution: object containing the objective function value (or an :class:`Infeasible`
            value) and *optional* solution data.
        """
        raise NotImplementedError()

    def backpropagate(self, sol):
        """Integrate the solution obtained by this node's simulation into its subtree.

        This updates sim_count and sim_best in all ancestor nodes.
        """
        assert self.sim_count == 0
        self.sim_count = 1
        self.sim_sol = sol
        self.sim_best = sol
        for ancestor in self.path:
            ancestor.sim_count += 1
            if ancestor.sim_best.value > sol.value:
                ancestor.sim_best = sol

    def delete(self):
        """Remove a leaf or an entire subtree from the search tree, updating its ancestors' stats.

        This method unlinks the node from its parent, and also removes its simulation result from
        all the nodes in its path, which is roughly equivalent to the opposite of backpropagate().
        Note that nodes in the path *must* be updated in bottom-up order.
        Note also that deletion of a node may trigger the deletion of its parent.
        """
        node = self
        while True:
            # Keep references to the path and parent since they'd be lost after remove_child().
            bottom_up_path = reversed(node.path)
            parent = node.parent
            # Unlink node from parent.
            if parent is not None:
                parent.remove_child(node)
            # Update sim_best for all ancestor nodes (bottom-up order!).
            for ancestor in bottom_up_path:
                if ancestor.sim_best is not node.sim_best:
                    break
                # New ancestor sim_best is the best of children's sim_best or its own sim_sol.
                candidates = [child.sim_best for child in ancestor.children]
                candidates.append(ancestor.sim_sol)
                ancestor.sim_best = min(candidates, key=lambda s: s.value)
            # Propagate deletion to parent if it exists (true for all nodes except root) and has
            # become exhausted (i.e. is fully expanded and has no more children).
            if parent is None or not parent.is_exhausted:
                break
            node = parent

    # Branch-and-bound/pruning- related methods
    def prune(self, cutoff):
        """Called on the root node to prune off nodes/subtrees which can no longer lead to a
        solution better than the best solution found so far.
        """
        stack = [self]
        while len(stack) > 0:
            node = stack.pop()
            if node.bound() >= cutoff:
                node.delete()
            elif node.is_expanded:
                stack.extend(node.children)

    def bound(self):
        """Compute a lower bound on the current subtree's optimal objective value.

        A :meth:`bound` method shoud be defined in subclasses intending to use pruning. By
        default, pruning will be automatically activated if the root node defines a :meth:`bound`
        method different from the one defined in the base :class:`TreeNode` class.

        Returns:
            a lower bound on the optimal objective function value in the subtree under the
            current node.
        """
        raise NotImplementedError()


def max_elems(iterable, key=None):
    """Find the elements in 'iterable' corresponding to the maximum values w.r.t. 'key'."""
    iterator = iter(iterable)
    try:
        elem = next(iterator)
    except StopIteration:
        raise ValueError("argument iterable must be non-empty")
    max_elems = [elem]
    max_key = elem if key is None else key(elem)
    for elem in iterator:
        curr_key = elem if key is None else key(elem)
        if curr_key > max_key:
            max_elems = [elem]
            max_key = curr_key
        elif curr_key == max_key:
            max_elems.append(elem)
    return max_elems


def config_logging(name=__name__, level="INFO"):
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            },
        },
        'handlers': {
            'default': {
                'level': level,
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            name: {
                'handlers': ['default'],
                'level': level,
                'propagate': True,
            },
        }
    })
