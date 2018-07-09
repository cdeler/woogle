import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run wiki-downloader&parser')

    parser.add_argument('script', type=str, help='running script')
    parser.add_argument('url',type=str, help='url to download from')

    args = parser.parse_args()

    print('\n')
    print(args)



