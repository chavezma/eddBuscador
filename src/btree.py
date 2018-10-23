import bisect
import queue
from collections import deque

class BTreeNode(object):

    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.c = []
        self.p = []

    def __str__(self):
        if self.leaf:
            return "Leaf K:{0}".format(self.keys)
            #return "Leaf {0} keys\n\tK:{1}\n\tC:{2}\n".format(len(self.keys), self.keys, self.c)
        else:
            return "Internal K:{0}".format(self.keys)
            #return "Internal {0} keys, {1} children\n\tK:{2}\n\n".format(len(self.keys), len(self.c), self.keys, self.c)


class BTree(object):
    def __init__(self, t):
        self.root = BTreeNode(leaf=True)
        self.t = t

    def search(self, k, x=None):

        if isinstance(x, BTreeNode):
            i = 0
            while i < len(x.keys) and k > x.keys[i]:  # look for index of k
                i += 1
            if i < len(x.keys) and k == x.keys[i]:  # found exact match
                return x, i
            elif x.leaf:  # no match in keys, and is leaf ==> no match exists
                return None, 0
            else:  # search children
                return self.search(k, x.c[i])
        else:  # no node provided, search root of tree
            return self.search(k, self.root)

    def insert(self, k):
        r = self.root
        if len(r.keys) == self.t - 1:  # keys are full, so we must split
            s = BTreeNode()
            self.root = s
            s.c.insert(0, r)  # former root is now 0th child of new root s
            self._split_child(s, 0)
            self._insert_nonfull(s, k)
        else:
            self._insert_nonfull(r, k)

    def _insert_nonfull(self, x, k):
        i = len(x.keys) - 1
        if x.leaf:
            # insert a key
            x.keys.append(0)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                i -= 1
            x.keys[i + 1] = k
        else:
            # insert a child
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.c[i].keys) == self.t - 1:
                self._split_child(x, i)
                if k > x.keys[i]:
                    i += 1
            self._insert_nonfull(x.c[i], k)

    def _split_child(self, nodo_padre, pos_hijo):
        # Obtengo la posicion central (medio)
        medio = (self.t - 1)//2
        # Nodo que quiero partir
        nodo_hijo = nodo_padre.c[pos_hijo]
        # Nuevo nodo (sibling) que sera hoja si el nodo a partir era hoja
        nuevo_nodo = BTreeNode(leaf=nodo_hijo.leaf)

        # Agrego el nodo "sibling" como hijo del padre
        nodo_padre.c.insert(pos_hijo + 1, nuevo_nodo)
        # Al partir el elemendo "medio" del nodo, pasa a ser la clave del padre.
        nodo_padre.keys.insert(pos_hijo, nodo_hijo.keys[medio])

        # El hermano derecho, se queda con los elementos "derechos"
        nuevo_nodo.keys = nodo_hijo.keys[medio:]
        # El hermano izquierdo, se queda con los elementos "izquierdo"
        nodo_hijo.keys = nodo_hijo.keys[0:medio]

        # children of z are t to 2t els of y.c
        if not nodo_hijo.leaf:
            nuevo_nodo.c = nodo_hijo.c[medio:]
            nodo_hijo.c = nodo_hijo.c[0:medio]

    def __str__(self):
        r = self.root
        output = ""
        open_set = deque()
        open_set.append(r)

        while open_set:
            subtree_root = open_set.popleft()
            output = subtree_root.__str__() + "\n"
            for child in subtree_root.c:
                output = output + " - " + child.__str__()
                if not child.leaf:
                    open_set.append(child)

        return output


if __name__ == '__main__':

    myArbol = BTree(3)
    mynodo = BTreeNode()
    Key = 0

    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad"
    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad, memorización, etc. También puede servir para juegos"
    palabras = "Bienvenidos al creador de palabras"
    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad, memorización, etc. También puede servir para juegos con niños, por ejemplo, una persona puede generar una palabra sin que otras la vean, hace un dibujo y las otras personas tienen que adivinar cuál es la palabra."
    print("insertando elementos....")

    for pal in palabras.split():
        print("Insertando palabra [{}]".format(pal))
        myArbol.insert(pal.lower())

    # myArbol.insertar("cosa");
    # myArbol.insertar("puerta");
    # myArbol.insertar("sabroso");
    # myArbol.insertar("abierto");
    # myArbol.insertar("terraza");
    # myArbol.insertar("delfin");
    # myArbol.insertar("casa");

    print(myArbol)

    # for bus in ["palabras", "sera"]:
    #     print("\nbuscando elemento {}...\n", bus)
    #     mynodo, Key = myArbol.buscar(bus)
    #     if mynodo2 is None:
    #         print("no encontro\n")
    #     else:
    #         print("encontro\n")
