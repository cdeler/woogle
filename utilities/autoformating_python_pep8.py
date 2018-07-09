import sys

def main(argv=None, apply_config=True):
    try:
        import autopep8
    except Exception:
        print("Error: can't import autopep8")
        return 1

    if argv is None:
        argv = sys.argv

    autopep8.main(["autopep8","--in-place", "--aggressive", "--aggressive"] + argv[1:])
    return 0


if __name__ == '__main__':
    sys.exit(main())
