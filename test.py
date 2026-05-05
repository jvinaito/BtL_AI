import heapq, random, time, csv, math
from collections import deque

OBSTACLE, EMPTY = 1, 0

def heuristic_manhattan(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
def heuristic_euclidean(a,b): return math.hypot(a[0]-b[0], a[1]-b[1])
def heuristic_diagonal(a,b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

def get_neighbors(pos,grid,height,width):
    r,c=pos; neigh=[]
    for dr,dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
        nr,nc=r+dr,c+dc
        if 0<=nr<height and 0<=nc<width:
            if dr!=0 and dc!=0:
                if grid[r+dr][c]==OBSTACLE or grid[r][c+dc]==OBSTACLE: continue
            neigh.append((nr,nc))
    return neigh

def greedy_step(open_heap,closed,parent,grid,goal,heur,height,width):
    if not open_heap: return "fail"
    _,cur=heapq.heappop(open_heap)
    if cur==goal: return "found"
    closed.add(cur)
    for nb in get_neighbors(cur,grid,height,width):
        r,c=nb
        if grid[r][c]!=OBSTACLE and nb not in closed:
            if not any(nb==item[1] for item in open_heap):
                parent[nb]=cur
                heapq.heappush(open_heap, (heur(nb,goal), nb))
    return "continue"

def reconstruct_path(parent,start,goal):
    path=[]; cur=goal
    while cur!=start:
        path.append(cur); cur=parent.get(cur)
        if cur is None: return []
    path.append(start); path.reverse(); return path

def solve(heur,grid,start,goal,height,width,timeout=5.0):
    st=time.time()
    open_heap,closed,parent=[],set(),{}
    heapq.heappush(open_heap,(heur(start,goal),start))
    while open_heap:
        if time.time()-st>timeout: return None,None,None
        res=greedy_step(open_heap,closed,parent,grid,goal,heur,height,width)
        if res=="found":
            path=reconstruct_path(parent,start,goal)
            return path,len(closed),time.time()-st
        elif res=="fail": return None,None,None
    return None,None,None

def generate_random_map(h,w,start,goal,density):
    grid=[[EMPTY]*w for _ in range(h)]
    cells=[(r,c) for r in range(h) for c in range(w) if (r,c) not in (start,goal)]
    random.shuffle(cells)
    for i in range(int(h*w*density)):
        r,c=cells[i]; grid[r][c]=OBSTACLE
    grid[start[0]][start[1]]=EMPTY; grid[goal[0]][goal[1]]=EMPTY
    return grid

def is_reachable(grid,start,goal,h,w):
    q=deque([start]); visited={start}
    while q:
        r,c=q.popleft()
        if (r,c)==goal: return True
        for dr,dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr,nc=r+dr,c+dc
            if 0<=nr<h and 0<=nc<w and grid[nr][nc]!=OBSTACLE and (nr,nc) not in visited:
                visited.add((nr,nc)); q.append((nr,nc))
    return False

def run():
    heur_map={'Manhattan':heuristic_manhattan,'Euclidean':heuristic_euclidean,'Diagonal':heuristic_diagonal}
    sizes=[(15,20),(20,30)]; densities=[0.2,0.3,0.4]; tests=30
    results=[]
    for h,w in sizes:
        for dens in densities:
            for name,func in heur_map.items():
                print(f"Running {name}, {w}x{h}, density={dens}")
                succ=0
                for _ in range(tests):
                    start=(0,0); goal=(h-1,w-1)
                    grid=generate_random_map(h,w,start,goal,dens)
                    if not is_reachable(grid,start,goal,h,w): continue
                    path,nodes,t=solve(func,grid,start,goal,h,w,timeout=10)
                    if path:
                        succ+=1
                        results.append({'heuristic':name,'size':f"{w}x{h}",'density':dens,
                                        'path_length':len(path),'nodes_expanded':nodes,'time_sec':t})
                print(f"  => success {succ}/{tests}")
    with open('results_pathfinding.csv','w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['heuristic','size','density','path_length','nodes_expanded','time_sec'])
        writer.writeheader(); writer.writerows(results)
    print("Done. Saved results_pathfinding.csv")

if __name__=='__main__': run()