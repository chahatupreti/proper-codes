g=open('F:\M.Tech\org segregated\mus musculus\mouse_keywords.txt','r').readlines()
r = open('F:\M.Tech\org segregated\mus musculus\mouse_keywords1.txt','w')
for f in g:
    #print f
    f = f.lstrip().rstrip()
    r.write(f)
    r.write('\n')
    #print f
r.close()
