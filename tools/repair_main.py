import sys, os
p='backend/main.py'
backup=p+'.bak'
print('Backing up',p,'->',backup)
if not os.path.exists(backup):
    os.rename(p,backup)
else:
    print('Backup already exists')
    # read original from backup
    os.remove(p)

b=open(backup,'rb').read()
idx=b.find(b'\x00')
if idx==-1:
    print('No null bytes found, nothing to do')
    sys.exit(0)
print('First null at',idx)
# Try decode tail as utf-16-le
tail=b[idx:]
try:
    tail_text=tail.decode('utf-16-le')
    print('Tail decoded as utf-16-le, length',len(tail_text))
    head_text=b[:idx].decode('utf-8',errors='ignore')
    new_text=head_text+tail_text
    open(p,'w',encoding='utf-8').write(new_text)
    print('Repaired file written to',p)
except Exception as e:
    print('utf-16-le decode failed:',e)
    # Fallback: strip all nulls and decode as utf-8
    cleaned=b.replace(b'\x00',b'')
    try:
        open(p,'w',encoding='utf-8').write(cleaned.decode('utf-8',errors='ignore'))
        print('Wrote cleaned file by removing NULs')
    except Exception as e2:
        print('Failed to clean file:',e2)
        sys.exit(2)
