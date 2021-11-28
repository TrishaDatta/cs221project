def get_masks():
    urlsWithLinks = set()
    with open('urlToNodeNumber.txt', encoding="utf8") as nodefile:
        lines = nodefile.readlines()
        for line in lines:
            cels = line.strip().split(' , ')
            url = cels[0].lower()
            urlsWithLinks.add(url)

    train_fake_urls = None
    train_real_urls = None
    test_fake_urls = None
    test_real_urls = None

    with open('train_fake_urls', encoding="utf8") as datafile:
         train_fake_urls = [line.strip().lower() for line in datafile.readlines()]

    with open('train_real_urls', encoding="utf8") as datafile:
         train_real_urls = [line.strip().lower() for line in datafile.readlines()]

    with open('test_fake_urls', encoding="utf8") as datafile:
         test_fake_urls = [line.strip().lower() for line in datafile.readlines()]

    with open('test_real_urls', encoding="utf8") as datafile:
         test_real_urls = [line.strip().lower() for line in datafile.readlines()]

    train_urls = train_fake_urls + train_real_urls
    test_urls = test_fake_urls + test_real_urls

    train_mask = []
    for url in train_urls:
        if url in urlsWithLinks:
            train_mask.append(True)
        else:
            train_mask.append(False)

    test_mask = []
    for url in test_urls:
        if url in urlsWithLinks:
            test_mask.append(True)
        else:
            test_mask.append(False)

    return train_mask, test_mask

def mask_lists(list_to_mask, mask):
    ret = []
    for i in range(len(mask)):
        if mask[i]:
            ret.append(list_to_mask[i])
    return ret

def get_final_lists(train_labels, train_set, test_labels, test_set):
    train_mask, test_mask = get_masks()
    new_train_labels = mask_lists(train_labels, train_mask)
    new_train_set = mask_lists(train_set, train_mask)
    new_test_labels = mask_lists(test_labels, test_mask)
    new_test_set = mask_lists(test_set, test_mask)
    return new_train_labels, new_train_set, new_test_labels, new_test_set      
