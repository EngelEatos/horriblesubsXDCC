"""packagehelper"""
from random import choice

def get_best_package(packages, episode, ranking):
    """get best package by bot ranking or random"""
    for bot in ranking:
        for package in packages[episode]:
            if package["bot"] == bot:
                return package
    return choice(packages[episode])

def get_diff_episodes(packages, local):
    """return the difference between the folder of packages and local"""
    result = []
    packages = get_ep_size_tuple(packages)
    for package in packages:
        episode = package[0]
        size = int(package[1])
        if episode in local:
            local_size = int(local[episode][0]["size"] / (1024 * 1024))
            if size - 5 <= local_size <= size + 5:
                continue
        result.append(episode)
    return sorted(result)


def get_ep_size_tuple(packages):
    """return a list of (ep, size) of the packages"""
    return list(set([ (ep, packages[0]["size"]) for ep, packages in packages.items()]))


def group_by_ep(packages):
    """groups packages by id as dict and filter only latest versions"""
    result = {}
    for package in packages:
        if package["episode"] not in result:
            result[package["episode"]] = []
        result[package["episode"]].append(package)
    # remove lower version
    for ep, packages in result.items():
        version = max([v["version"][1:] for v in packages])
        if not version:
            continue
        filtered = list(filter(lambda item: item["version"][1:] == version, packages))
        result[ep] = filtered
    return result