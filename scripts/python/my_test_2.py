import time

def test():
    createTree()

if __name__ == '__main__':
    for i in range(100):
        print 'ALF_PROGRESS {}%'.format(i)
        time.sleep(0.1)

    # grabovskiy::my_srcNode::1.0.3