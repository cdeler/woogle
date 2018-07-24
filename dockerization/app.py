import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run wiki-downloader&parser')

    parser.add_argument('-N', type=int, default=40, help='number of symbols')
    parser.add_argument('-path2file',type=str, help='path to file where save downloaded data')

    args = parser.parse_args()

    print('\n')
    print(args.N)



