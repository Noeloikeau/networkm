# AUTOGENERATED! DO NOT EDIT! File to edit: 00_graph_functions.ipynb (unless otherwise specified).

__all__ = ['ring', 'print_graph', 'parse_kwargs', 'give_nodes', 'give_edges', 'node_attrs', 'edge_attrs', 'node_data',
           'edge_data', 'argwhere', 'kwargwhere', 'where', 'convert_edges', 'relabel_graph', 'sort_graph']

# Cell
import warnings
with warnings.catch_warnings(): #ignore warnings
    warnings.simplefilter("ignore")
    import networkx as nx
    import numpy as np
    import sidis
    rng=sidis.RNG(0)
    import matplotlib.pyplot as plt
    import typing
    from typing import Optional, Tuple, Dict, Callable, Union, Mapping, Sequence, Iterable, Hashable, List, Any
    from collections import namedtuple

# Cell
def ring(N : int = 3,
         left : bool = True,
         right : bool = False,
         loop : bool = False):
    '''
    Return `g`, a ring topology networkx graph with `N` nodes.
    Booleans `left`, `right`, `loop` determine the directed edges.
    '''

    g=nx.MultiDiGraph()

    e=[]

    if left:
        e+=[(i,(i-1)%N) for i in range(N)]
    if right:
        e+=[(i,(i+1)%N) for i in range(N)]
    if loop:
        e+=[(i,i) for i in range(N)]

    g.add_nodes_from([i for i in range(N)])
    g.add_edges_from(e)

    return g

# Internal Cell
def table(iterable : Iterable, header : Iterable[str]):
    '''
    Creates a simple ASCII table from an iterable and a header.
    Modified from
    https://stackoverflow.com/questions/5909873/how-can-i-pretty-print-ascii-tables-with-python
    '''
    max_len = [len(x) for x in header]
    for row in iterable:
        row = [row] if type(row) not in (list, tuple) else row
        for index, col in enumerate(row):
            if max_len[index] < len(str(col)):
                max_len[index] = len(str(col))

    output = '|' + ''.join([h + ' ' * (l - len(h)) + '|' for h, l in zip(header, max_len)]) + '\n'

    for row in iterable:
        row = [row] if type(row) not in (list, tuple) else row
        output += '|' + ''.join([str(c) + ' ' * (l - len(str(c))) + '|' for c, l in zip(row, max_len)]) + '\n'

    return output


# Cell
def print_graph(g : nx.MultiDiGraph,
               string=False):
    '''
    Print the 'node', predecessors', and 'successors' for every node in graph `g`.
    The predecessors are the nodes flowing into a node,
    and the successors are the nodes flowing out.

    Example use:
        g=ring(N=3,left=True,right=True,loop=True)
        print_graph(g)
    '''
    data = [[n, list(g.predecessors(n)), list(g.successors(n))] for n in g.nodes]
    for i in range(len(data)):
        data[i][1]=', '.join([str(i) for i in data[i][1]])
        data[i][2]=', '.join([str(i) for i in data[i][2]])

    header=['Node', 'Predecessors', 'Successors']

    if not string:
        print(table(data,header))
    else:
        return table(data,header)


# Cell
def parse_kwargs(**kwargs):
    '''
    Evaluate delayed function calls by assigning
    attributes as (func, *arg) tuples.
    Parse keyword arguments with the convention that
    kwarg = tuple ( callable , *args) be returned as
    kwarg = callable ( *args).
    Example: kwargs = {a : (np.random.random,1)}
    becomes  kwargs = {a : np.random.random(1)}
    each time this func is called.
    '''
    newkwargs={k:v for k,v in kwargs.items()}
    for k,v in kwargs.items():
        if type(v) is tuple and callable(v[0]):
            if len(v)==1:
                newkwargs[k]=v[0]()
            else:
                newkwargs[k]=v[0](*v[1:])
    return newkwargs

# Cell
def give_nodes(g : nx.MultiDiGraph,
               data : Dict[Hashable,dict] = None,
               nodes : Iterable = None,
               **kwargs):
    '''
    Parse and apply any 'kwargs' to a set of 'nodes'.
    If given, 'data' is a dict-of-dicts keyed by node.
    The inner dict is given to the corresponding node.
    '''
    if nodes is None:
        nodes=g.nodes

    if kwargs:
        [sidis.give(g.nodes[n],**parse_kwargs(**kwargs)) for n in nodes]

    if data:
        for k,v in data.items():
            try:
                g.nodes[k].update(parse_kwargs(**v))
            except KeyError:
                pass


# Internal Cell
def parse_edges(edges : Union[tuple,List[tuple]],
                default_key : Hashable = 0
               ):
    '''
    Parse a single edge or list of edges
    into a list of 3-tuples for iterating over
    a MultiDiGraph, which requires keys.
    '''
    if type(edges) is tuple:
        edges=[edges]
    if type(edges) is not list:
        edges=list(edges)
    for i in range(len(edges)):
        if len(edges[i])==4: #discard data, last entry
            edges[i]=(edges[i][0],edges[i][1],edges[i][2])
        if len(edges[i])==2: #include key, 3rd entry
            edges[i]=(edges[i][0],edges[i][1],default_key)
    return edges

# Cell
def give_edges(g : nx.MultiDiGraph,
               data : Dict[Hashable,dict] = None,
               edges : Iterable = None,
               **kwargs):
    '''
    Parse and apply any 'kwargs' to a set of 'edges'.
    If given, 'data' is a dict-of-dicts keyed by edge.
    The inner dict is given to the corresponding edge.
    '''
    if edges is None:
        edges=g.edges

    edges = parse_edges(edges)

    if kwargs:
        [sidis.give(g.edges[e],**parse_kwargs(**kwargs)) for e in edges]

    if data:
        for k,v in data.items():
            try:
                g.edges[k].update(parse_kwargs(**v))
            except:
                pass

# Cell
def node_attrs(g):
    '''
    Unique node data keys.
    '''
    return list(set(sidis.flatten([list(t[-1].keys())
                        for t in list(g.nodes(data=True))])))

# Cell
def edge_attrs(g):
    '''
    Unique edge data keys.
    '''
    return list(set(sidis.flatten([list(t[-1].keys())
                        for t in list(g.edges(data=True))])))

# Cell
def node_data(g,*args):
    '''
    Return node attributes 'args' as an array.
    NOTE: The ordering of the array corresponds to the
    ordering of the nodes in the graph.
    '''
    if not args:
        args=node_attrs(g)

    node_data={}

    [sidis.give(node_data,str(arg),
                np.squeeze(np.array([sidis.get(g.nodes[n],arg) for n in g.nodes])))
        for arg in args]

    return node_data

# Cell
def edge_data(g,*args):
    '''
    Return edge attributes 'args' as an array.
    NOTE: The ordering of the array corresponds to the
    ordering of the edges in the graph.
    '''
    if not args:
        args=edge_attrs(g)

    edge_data={}

    [sidis.give(edge_data,str(arg), np.array([sidis.get(g.edges[e],arg) for e in g.edges]))
        for arg in args]

    return edge_data

# Cell
def argwhere(*args : List[np.ndarray]):
    '''
    Simplified version of np.argwhere for multiple arrays.
    Returns list of indices where args hold.
    '''
    with warnings.catch_warnings(): #ignore numpy warning
        warnings.simplefilter("ignore")
        if not args:
            return None
        elif len(args)==1:
            return list(np.ravel(np.argwhere(args[0])).astype(int))
        else:
            i=[] #indices
            for arg in args:
                res=list(np.ravel(np.argwhere(arg)).astype(int))
                i+=[res]
            if len(i)==1:
                i=i[0]
            if np.any(i):
                return list(i)

# Cell
def kwargwhere(g : nx.MultiDiGraph,**kwargs : Dict[str,Any]):
    '''
    Return the node and edges where
    the kwarg equalities hold in the graph.
    '''
    node_k=node_attrs(g)
    edge_k=edge_attrs(g)
    node_i=[]
    edge_i=[]
    for k,v in kwargs.items():
        n_i=[]
        e_i=[]
        if k in node_k:
            for n in g.nodes:
                if g.nodes[n].get(k)==v:
                    n_i+=[n]
            node_i+=[n_i]
        if k in edge_k:
            for e in g.edges:
                if g.edges[e].get(k)==v:
                    e_i+=[e]
            edge_i+=[e_i]

    if len(node_i)==1:
        node_i=node_i[0]
    if len(edge_i)==1:
        edge_i=edge_i[0]
    if node_i and edge_i:
        return node_i,edge_i
    elif node_i:
        return node_i
    elif edge_i:
        return edge_i

# Cell
def where(g,*args,**kwargs):
    '''
    Combine the 'argwhere' and 'kwargwhere' functions for the graph.
    '''
    arg_i=argwhere(*args)
    kwarg_i=kwargwhere(g,**kwargs)
    if arg_i and kwarg_i:
        return arg_i,kwarg_i
    elif arg_i:
        return arg_i
    elif kwarg_i:
        return kwarg_i

# Internal Cell
def parse_lengths(g : nx.MultiDiGraph,
                  edges : Union[tuple,List[tuple]],
                  lengths : Union[str,int,List[int]] = 1) -> Union[list,List[list]]:
    '''
    Convert `lengths` corresponding to attributes of each edge into a list of lists.
    `lengths` can be a single integer, an integer for each edge, or a string
    giving the edge attribute holding the length.
    '''
    if type(lengths) is int:
        lengths={e:lengths for e in edges}
    elif type(lengths) is str:
        lengths={e:g.edges[e].get(lengths) for e in edges}
    return lengths

# Cell
def convert_edges(g : nx.MultiDiGraph,
                  edges : Union[None,tuple,List[tuple]] = None,
                  lengths : Union[str,int,dict] = 1,
                  node_data : dict = {},
                  label : callable = lambda g,node,iterable : len(g)+iterable,
                  **edge_data
                 ):
    '''
    Converts `edges` in `g` to paths of the given `lengths`.
    The new paths follow a tree structure, and each new node
    inherits `node_data` and is labeled with `label`.
    The tree structure finds the roots (set of starting nodes)
    in the list of `edges`, and then creates trunks corresponding
    to the paths of maximum length for each node. Then, branches are
    added from the trunk to each of the leaves (terminal nodes),
    made from new nodes equal to the lengths associated with each path.
    '''

    #default to all edges
    if edges is None:
        edges=g.edges

    #parse args
    edges=parse_edges(edges=g.edges(keys=True),default_key=0)
    lengths=parse_lengths(g=g,edges=edges,lengths=lengths)

    #unique first nodes
    roots=set([e[0] for e in edges])

    #max path lengths on a per-starting node basis
    trunks={r:max([lengths[e] for e in g.out_edges(r,keys=True) if e in edges])
            for r in roots}

    #sort roots by longest trunk length to create largest trunks first
    roots=sorted(roots,
                 key=lambda r: trunks[r],
                 reverse=True)

    #terminal nodes for each branch
    leaves={r:list(g.successors(r)) for r in roots}

    #now build trunks, then create branches from trunk to edges
    for r in roots:
        trunk=[label(g,node=r,iterable=i) for i in range(trunks[r])]
        if trunk!=[]:
            nx.add_path(g,[r]+trunk,**parse_kwargs(**edge_data))
            give_nodes(g,nodes=trunk,**node_data)
            for edge,length in lengths.items():
                if edge[0]==r: #branch from root

                    if length==trunks[r]: #go to leaf using trunk endpoint
                        branch=[trunk[-1]]+[edge[1]]

                    else: #create new branch from somewhere in trunk
                        branch=[trunk[length-1]]+[edge[1]]

                    nx.add_path(g,branch,**g.edges[edge]) #apply old edge data

                    give_nodes(g,nodes=branch[:-1],**node_data)

    #trim old edges
    for e in edges:
        g.remove_edge(*e)


# Cell
def relabel_graph(g : nx.MultiDiGraph,
            mapping : Union[None,callable,dict] = None):
    '''
    Relabel nodes in place with desired 'mapping', and store the
    `mapping` and `inverse_mapping` as attributes of `g`.
    Can be called again without args to relabel to the original map,
    which switches the `mapping` and `inverse_mapping`.
    If `mapping` is None and `g` has no `mapping`,
    defaults to replacing nodes with integers.
    If `mapping` is None and `g` has a `mapping`, uses that.
    Otherwise, `mapping` is a callable or dict keyed with old node labels
    as keys and new node labels as values.
    '''
    if mapping is None:
        if not g.__dict__.get('mapping'):
            mapping={n:i for i,n in enumerate(g.nodes)}
        else:
            mapping=g.mapping

    elif callable(mapping):
        mapping=mapping(g)

    inverse_mapping={v:k for k,v in mapping.items()}
    def relabel_nodes(G, mapping):
        H = nx.MultiDiGraph()
        H.add_nodes_from(mapping.get(n, n) for n in G)
        H._node.update((mapping.get(n, n), d.copy()) for n, d in G.nodes.items())
        if G.is_multigraph():
            new_edges = [
                (mapping.get(n1, n1), mapping.get(n2, n2), k, d.copy())
                for (n1, n2, k, d) in G.edges(keys=True, data=True)
            ]

            # check for conflicting edge-keys
            undirected = not G.is_directed()
            seen_edges = set()
            for i, (source, target, key, data) in enumerate(new_edges):
                while (source, target, key) in seen_edges:
                    if not isinstance(key, (int, float)):
                        key = 0
                    key += 1
                seen_edges.add((source, target, key))
                if undirected:
                    seen_edges.add((target, source, key))
                new_edges[i] = (source, target, key, data)

            H.add_edges_from(new_edges)
        else:
            H.add_edges_from(
                (mapping.get(n1, n1), mapping.get(n2, n2), d.copy())
                for (n1, n2, d) in G.edges(data=True)
            )
        H.graph.update(G.graph)
        return H
    gnew=relabel_nodes(g,mapping)
    g.__dict__.update(gnew.__dict__)
    g.mapping=inverse_mapping
    g.inverse_mapping=mapping

# Cell
def sort_graph(g : nx.MultiDiGraph,
               nodes_by='in_degree', #g.in_degree, #sorting this function over nodes
               node_key=lambda t:sidis.get(t,-1,-1), #last element of sorting tuple
               node_args=(), #not accessing any attributes by default
               nodes_ascending=True,
               edges_by=None, #not generating function evals to sort
               edge_key=None,#orders edges, defaults to linear comb of node sort
               edge_args=(), #not accessing any edge attrs by default
               edges_ascending=False,
               relabel=False #relabel to integers
              ) -> None:
    '''
    Sort the graph in place by changing node and edge order.
    See `sidis.sort` documentation for explanation of by, key, and args.
    Default behavior is to sort nodes by in-degree, and edges by increasing node label,
    after relabling nodes to integers. Stores result in 'sorting' attribute.
    '''
    #parse args; get node sorting attr if str
    if type(nodes_by) is str:
        nodes_by=sidis.get(g,nodes_by)
    #if no edge key given default to ordering by linear comb of node func
    if edge_key is None:
        edge_key=lambda t:100*nodes_by(t[0])-10*nodes_by(t[1])

    #sort nodes
    node_sorting=sidis.sort(g.nodes,
                            *node_args,
                            by=nodes_by,
                            key=node_key,
                            reverse=nodes_ascending)

    #sort returns tuples of (node,nodes_by(node)), so extract nodes and data
    if nodes_by is None:
        nodes=[(n,g.nodes[n]) for n in node_sorting]
    else:
        nodes=[(n[0],g.nodes[n[0]]) for n in node_sorting]

    #sort edges
    edge_sorting=sidis.sort(list(g.edges(keys=True)),
                            *edge_args,
                            by=edges_by,
                            key=edge_key,
                            reverse=edges_ascending)

    #extract edge,data tuple
    if edges_by is None:
        edges=[(*e,g.edges[e]) for e in edge_sorting]
    else:
        edges=[(*e[0],g.edges[e[0]]) for e in edge_sorting]

    #wipe graph and add new nodes/edges in order
    g.clear()
    g.add_nodes_from(nodes)
    g.add_edges_from(edges)

    #relabel to new ranking if desired
    if relabel:
        mapping={n:i for i,n in enumerate([node[0] for node in nodes])}
        relabel_graph(g,mapping)
        new_node_sorting=[]
        for node,rank in node_sorting:
            new_node_sorting+=[(g.inverse_mapping[node],rank)]
        node_sorting=new_node_sorting

    sorting=nx.utils.groups(dict(node_sorting))
    g.sorting={k:list(v) for k,v in sorting.items()}