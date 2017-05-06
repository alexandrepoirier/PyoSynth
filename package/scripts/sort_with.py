def sort_with(src_list, ref, reverse=False):
    """
    Sorts a list according to the values in the dictionnary 'ref'.

    src_list : the list to sort
    ref : the reference dictionnary containing the values used for sorting
    reverse : if True, will sort from biggest to smallest
    
    ex. :
    src_list = [2,7,8,1]
    ref = {1:35, 2:68, 7:5, 8:3}
    sort_with() will return the following list : [8,7,1,2]
    """
    sorted = list(src_list)
    temp = 0
    len_list = len(sorted)
    if not reverse:
        for i in range(len_list-1):
            small_ind = i
            for j in range(i+1, len_list):
                if dict[sorted[j]] < dict[sorted[small_ind]]:
                    small_ind = j
            if small_ind != i:
                temp = sorted[i]
                sorted[i] = sorted[small_ind]
                sorted[small_ind] = temp
    else:
        for i in range(len_list-1):
            big_ind = i
            for j in range(i+1, len_list):
                if dict[sorted[j]] > dict[sorted[big_ind]]:
                    big_ind = j
            if big_ind != i:
                temp = sorted[i]
                sorted[i] = sorted[big_ind]
                sorted[big_ind] = temp
    return sorted

if __name__ == "__main__":
    import random

    src = [random.randint(0,127) for i in range(10)]
    dict = {}
    for key in src:
        dict[key] = random.randint(0,127)

    print sort_with(src, dict)