def dedupe_lists(list1, list2, count=100):
    ordered_list = sorted(list1 + list2, key=lambda k: k['id'], reverse=True)
    deduped_list = []
    deduped_items = []
    deduped_count = 0
    for item in ordered_list:
        if item['id'] not in deduped_items and deduped_count < count:
            deduped_list.append(item)
            deduped_items.append(item['id'])
            deduped_count += 1
    return deduped_list