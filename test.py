from multiprocessing import Pool, Manager, freeze_support
from queue import Queue


def download(cmd, q):
    """downlaod files"""
    print(q.get())
    return cmd


def start():
    """run"""
    cmds = ['PRIVMSG CR - RALEIGH | NEW :xdcc send #379']
    q = Manager().Queue()
    print("tasks: " + str(cmds))
    print("setup pools")
    q.put("abc")
    pool = Pool(processes=1)
    for result in pool.imap_unordered(download, cmds[0], q, 1):
        print(result)


def main():
    start()


if __name__ == '__main__':
    freeze_support()
    main()
