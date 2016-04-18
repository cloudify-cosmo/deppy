
def cmp_elements(e1, e2):
    if type(e1) != type(e2):
        return False
    if isinstance(e1, list):
        return cmp_unordered_lists(e1, e2)
    if isinstance(e1, dict):
        return cmp_dicts(e1, e2)
    if isinstance(e1, tuple):
        return cmp_tuples(e1, e2)
    if isinstance(e1, set):
        return cmp_sets(e1, e2)
    return e1 == e2


def cmp_unordered_lists(list1, list2):
    if len(list1) != len(list2):
        return False
    for element in list1:
        if not len([e for e in list2 if cmp_elements(e, element)]):
            return False
    for element in list2:
        if not len([e for e in list1 if cmp_elements(e, element)]):
            return False
    return True


def cmp_sets(set1, set2):
    if len(set1) != len(set2):
        return False
    for element in set1:
        if element not in set2:
            return False
    return True


def cmp_tuples(tuple1, tuple2):
    if len(tuple1) != len(tuple2):
        return False
    for i in range(len(tuple1)):
        if not cmp_elements(tuple1[i], tuple2[i]):
            return False
    return True


def cmp_dicts(dic1, dic2):
    if len(dic1) != len(dic2):
        return False
    for element in dic1:
        if element not in dic2:
            return False
        if not cmp_elements(dic1[element], dic2[element]):
            return False
    return True
