def dedupe_lists(list1, list2, count=100):
    ordered_list = sorted(list1 + list2, key=lambda k: k['published'], reverse=True)
    deduped_list = []
    deduped_items = 0
    for item in (ordered_list):
        if item not in deduped_list and deduped_items < count:
            deduped_list.append(item)
            deduped_items += 1
    return deduped_list