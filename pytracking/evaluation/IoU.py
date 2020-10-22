def cal_iou(bbox1, bbox2):
    """[summary]

    :param bbox1: [description]
    :type bbox1: list
    :param bbox2: [description]
    :type bbox2: list
    """
    l1, d1 = bbox1[0], bbox1[1]
    r1, u1 = l1 + bbox1[2], d1 + bbox1[3]
    s1 = bbox1[2] * bbox1[3]

    l2, d2 = bbox2[0], bbox2[1]
    r2, u2 = l1 + bbox2[2], d1 + bbox2[3]
    s2 = bbox2[2] * bbox2[3]

    l, r = max(l1, l2), min(r1, r2)
    d, u = max(d1, d2), min(u1, u2)

    if l < r and d < u: si = (r - l) * (u - d)
    else: si = 0.0

    return si / (s1 + s2 - si)