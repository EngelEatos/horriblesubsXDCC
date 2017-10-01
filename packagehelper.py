from random import randint


def get_episode_package(packages, episode, default_bot):
    """get availible package of episode, first default then random"""
    (result, version_result) = get_packages_by_ep(packages, episode)
    packages = get_latest_packages(
        version_result) if version_result else result
    return get_packages(packages, default_bot)


def get_packages(packages, default_bot):
    """get matching package"""
    selected = []
    for package in packages:
        if package[0] == default_bot:
            return package
        else:
            selected.append(package)
    return selected[randint(0, len(selected) - 1)]


def get_latest_packages(version_result):
    """return latest package, use versioning"""
    packs = []
    version_max = 0
    for result in version_result:
        version = int(result[3][3][1:])
        if version < version_max:
            continue
        if version > version_max:
            packs.clear()
            version_max = version
        packs.append(result)
    return packs


def get_packages_by_ep(packages, episode):
    """return package by episode number"""
    result = []
    version_result = []
    for package in packages:
        if package[3][2] == episode:
            if package[3][3]:
                version_result.append(package)
            else:
                result.append(package)
    return (result, version_result)


def get_diff_episodes(packages, local):
    """return the difference between the folder of packages and local"""
    todo = []
    local_eps = [l[0][2] for l in local]
    packages = distinct_packages(packages)
    for package in packages:
        episode = package[3][2]
        size = int(package[2])
        if episode in local_eps:
            local_size = int(get_size(local, episode) / (1024 * 1024))
            # print(str(size) + " =?= " + str(local_size))
            if size - 50 <= local_size <= size + 50:
                continue
        todo.append(episode)
    return todo


def distinct_packages(packages):
    """return a distinct list of the packages"""
    result = []
    eps = []
    for package in packages:
        if package[3][2] not in eps:
            eps.append(package[3][2])
            result.append(package)
    return result


def get_size(local, episode):
    """return the size of ep in local episodes"""
    for local_ep in local:
        if local_ep[0][2] == episode:
            return local_ep[1]
    return -1
