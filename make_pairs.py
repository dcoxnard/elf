from typing import List, Dict
import random
from copy import deepcopy


# TODO: would be more generalizable to just have the list of items,
# and a map described what is not allowed to be allocated to what.
# Levels of abstraction are getting mixed together with this.
def make_pairs(items: List, partition: Dict, not_allowed_map: Dict):
    """
    Docstring here!

    :param items: List[item]
    :param partition: Dict[str: str] e.g. "bob" --> "smith"
        Maps each item to its group.
    :param: not_allowed_map: Dict[str: str]
    :return: List[List[item, item]]
    """
    # This works!
    # Returns an ordered list of pairs.
    # The results are stochastic.
    # It may result in a "bipartite graph" ie where there are
    # e.g. 2+ "little" cycles rather than one "big" one

    # Degenerate case
    if len(items) == 0:
        return []

    acc = []

    def go(a, b, inner=[]):
        """
        Stateful!

        Relies on outer scope `acc` and `partition`
        :param a: List[item]
        :param b: List[item]
        :param inner: List
        :return: None
        """

        if len(inner) == len(items):
            acc.append(inner)
            return

        if len(acc) > 0:
            return

        else:
            random.shuffle(a)
            random.shuffle(b)
            for aa in a:
                for bb in b:
                    same_partition = partition[aa] == partition[bb]
                    not_allowed = not_allowed_map.get(aa) == bb
                    if same_partition or not_allowed:
                        continue
                    else:
                        new_a = [aaa for aaa in a if aaa != aa]
                        new_b = [bbb for bbb in b if bbb != bb]
                        new_inner = inner + [[aa, bb]]
                        go(new_a, new_b, new_inner)

    a = deepcopy(items)
    b = deepcopy(items)
    go(a, b)

    if not acc:
        raise RuntimeError("No pairings found")
    elif len(acc) > 1:
        raise RuntimeError(acc)

    # Put results in pair-order
    result = acc[0]
    ordered_result = [result.pop()]
    while result:
        ix = None
        for i, item in enumerate(result):
            if item[0] == ordered_result[-1][1]:
                ix = i
                break
        if ix is None:  # Bipartite graph -- just start over at 0
            ix = 0
        next_elem = result.pop(ix)
        ordered_result.append(next_elem)
    return ordered_result
