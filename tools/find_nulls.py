import os

root = os.path.join(os.getcwd(), 'backend')
null_files = []
for dirpath, dirnames, filenames in os.walk(root):
    for fname in filenames:
        path = os.path.join(dirpath, fname)
        try:
            with open(path, 'rb') as f:
                data = f.read()
                if b'\x00' in data:
                    null_files.append(path)
        except Exception as e:
            print('ERR', path, e)

if null_files:
    print('NULL FILES FOUND:')
    for p in null_files:
        print(p)
else:
    print('No null bytes found in files under', root)
