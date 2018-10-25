import bisect
import queue
from collections import deque

class BTreeNode(object):

    def __init__(self, es_hoja=False):
        self.es_hoja = es_hoja
        self.claves = []
        self.hijos = []
        self.padre = None

    def __str__(self):
        if self.es_hoja:
            return "Leaf K:{0}".format(self.claves)
            #return "Leaf {0} keys\n\tK:{1}\n\tC:{2}\n".format(len(self.keys), self.keys, self.c)
        else:
            return "Internal K:{0}".format(self.claves)
            #return "Internal {0} keys, {1} children\n\tK:{2}\n\n".format(len(self.keys), len(self.c), self.keys, self.c)


class BTree(object):
    def __init__(self, orden):
        self.root = BTreeNode(es_hoja=True)
        self.orden = orden

    def path_to(self, k, el_nodo=None):
        # Si especifico un nodo arranco a buscar desde ahi.
        if isinstance(el_nodo, BTreeNode):
            idx = 0
            # En el nodo actual, busco la posicion donde deberia estar la clave.
            while idx < len(el_nodo.claves) and k > el_nodo.claves[idx]:
                idx += 1
            # Si salgo del while es porque o encontre la posicion, o estoy en la ultima clave del nodo.
            if idx < len(el_nodo.claves) and k == el_nodo.claves[idx]:
                # Si encontre la clave, es repetido.
                # Si el i >= 0 entonces seria un elemento duplicado
                return el_nodo, idx
            elif el_nodo.es_hoja:
                # Si recorrio todo el nodo y es una hoja, estoy en el nodo donde deberia ir la clave.
                return el_nodo, -1
            else:  # No lo encontre, y no es una hoja, entonces sigo mirando la rama correspondiente
                return self.path_to(k, el_nodo.hijos[idx])
        else:  # no node provided, search root of tree
            return self.path_to(k, self.root)

    def new_insert(self, k):
        el_nodo, idx = self.path_to(k)

        if idx >= 0:
            # Si el indice es mayor o igual que cero, quiere decir que el elemento ya existe
            # retorno el nodo donde deberia de haberse insertado y el valor de -1 para enfatizar esto.
            return el_nodo, -1

        if len(el_nodo.claves) == self.orden - 1:  # keys are full, so we must split
            if isinstance(el_nodo.padre, BTreeNode):
                # Si ya tiene un padre, listo
                el_padre = el_nodo.padre
            else:
                # Si no tiene padre, era la raiz
                # Creo un nuevo nodo
                el_padre = BTreeNode()
                # Sera el nuevo root.
                self.root = el_padre
                # Como tengo un nuevo padre, agrego el nodo objetivo como su primer hijo.
                el_padre.hijos.append(el_nodo)

            self._split_hoja(el_padre, len(el_padre.hijos)-1, k)

            if len(el_padre.claves) == self.orden:
                self._grow(el_padre)
        else:
            bisect.insort_right(el_nodo.claves, k)

        # Retorno el nodo y el valor de la clave para enfatizar que pudo insertarse
        return el_nodo, k

    def _grow(self, rama):
        if isinstance(rama.padre, BTreeNode):
            # Si ya tiene un padre, listo
            el_padre = rama.padre
        else:
            # Si no tiene padre, era la raiz
            # Creo un nuevo nodo
            el_padre = BTreeNode()
            # Sera el nuevo root.
            self.root = el_padre
            # Como tengo un nuevo padre, agrego el nodo objetivo como su primer hijo.
            el_padre.hijos.append(rama)

        self._split_interno(el_padre, len(el_padre.hijos) - 1)

        if len(el_padre.claves) == self.orden:
            self._grow(el_padre)

    def _split_interno(self, padre, pos_hijo):
        # Obtengo la posicion central (medio)
        medio = (self.orden - 1)//2
        # Nodo que quiero partir
        nodo_hijo = padre.hijos[pos_hijo]
        # Nuevo nodo (sibling) que sera hoja si el nodo a partir era hoja
        nuevo_nodo = BTreeNode(es_hoja=nodo_hijo.es_hoja)
        # Agrego el nodo "sibling" como hijo del padre
        padre.hijos.insert(pos_hijo + 1, nuevo_nodo)
        # Al partir el elemendo "medio" del nodo, pasa a ser la clave del padre.
        padre.claves.insert(pos_hijo, nodo_hijo.claves[medio])

        # El hermano derecho, se queda con los elementos "derechos"
        nuevo_nodo.claves = nodo_hijo.claves[medio+1:]
        nuevo_nodo.padre = padre
        # El hermano izquierdo, se queda con los elementos "izquierdo"
        nodo_hijo.claves = nodo_hijo.claves[0:medio]
        nodo_hijo.padre = padre

        if not nodo_hijo.es_hoja:

            nuevo_nodo.hijos = nodo_hijo.hijos[medio+1:]
            for hijo in nuevo_nodo.hijos:
                hijo.padre = nuevo_nodo

            nodo_hijo.hijos = nodo_hijo.hijos[0:medio+1]
            for hijo in nodo_hijo.hijos:
                hijo.padre = nodo_hijo

    def _split_hoja(self, padre, pos_hijo, k):
        # Obtengo la posicion central (medio)
        medio = (self.orden - 1)//2
        # Nodo que quiero partir
        nodo_hijo = padre.hijos[pos_hijo]
        # De manera auxiliar, inserto la clave
        bisect.insort_right(nodo_hijo.claves, k)
        # Nuevo nodo (sibling) que sera hoja si el nodo a partir era hoja
        nuevo_nodo = BTreeNode(es_hoja=nodo_hijo.es_hoja)
        # Agrego el nodo "sibling" como hijo del padre
        padre.hijos.insert(pos_hijo + 1, nuevo_nodo)
        # Al partir el elemendo "medio" del nodo, pasa a ser la clave del padre.
        padre.claves.insert(pos_hijo, nodo_hijo.claves[medio])

        # El hermano derecho, se queda con los elementos "derechos"
        nuevo_nodo.claves = nodo_hijo.claves[medio:]
        nuevo_nodo.padre = padre
        # El hermano izquierdo, se queda con los elementos "izquierdo"
        nodo_hijo.claves = nodo_hijo.claves[0:medio]
        nodo_hijo.padre = padre

        if not nodo_hijo.es_hoja:
            nuevo_nodo.hijos = nodo_hijo.hijos[medio:]
            for hijo in nuevo_nodo.hijos:
                hijo.padre = nuevo_nodo

            nodo_hijo.hijos = nodo_hijo.hijos[0:medio]
            for hijo in nodo_hijo.hijos:
                hijo.padre = nodo_hijo

    def _insert_nonfull(self, x, k):
        i = len(x.claves) - 1
        if x.es_hoja:
            # insert a key
            x.claves.append(0)
            while i >= 0 and k < x.claves[i]:
                x.claves[i + 1] = x.claves[i]
                i -= 1
            x.claves[i + 1] = k
        else:
            # insert a child
            while i >= 0 and k < x.claves[i]:
                i -= 1
            i += 1
            if len(x.c[i].claves) == self.orden - 1:
                self._split_child(x, i)
                if k > x.claves[i]:
                    i += 1
            self._insert_nonfull(x.c[i], k)

    def search(self, k, x=None):

        if isinstance(x, BTreeNode):
            i = 0
            while i < len(x.claves) and k > x.claves[i]:  # look for index of k
                i += 1
            if i < len(x.claves) and k == x.claves[i]:  # found exact match
                return x, i
            elif x.es_hoja:  # no match in keys, and is leaf ==> no match exists
                return None, 0
            else:  # search children
                return self.search(k, x.c[i])
        else:  # no node provided, search root of tree
            return self.search(k, self.root)

    def _split_child(self, nodo_padre, pos_hijo):
        # Obtengo la posicion central (medio)
        medio = (self.orden - 1)//2
        # Nodo que quiero partir
        nodo_hijo = nodo_padre.c[pos_hijo]
        # Nuevo nodo (sibling) que sera hoja si el nodo a partir era hoja
        nuevo_nodo = BTreeNode(es_hoja=nodo_hijo.es_hoja)

        # Agrego el nodo "sibling" como hijo del padre
        nodo_padre.hijos.insert(pos_hijo + 1, nuevo_nodo)
        # Al partir el elemendo "medio" del nodo, pasa a ser la clave del padre.
        nodo_padre.claves.insert(pos_hijo, nodo_hijo.claves[medio])

        # El hermano derecho, se queda con los elementos "derechos"
        nuevo_nodo.claves = nodo_hijo.claves[medio:]
        # El hermano izquierdo, se queda con los elementos "izquierdo"
        nodo_hijo.claves = nodo_hijo.claves[0:medio]

        # children of z are t to 2t els of y.c
        if not nodo_hijo.es_hoja:
            nuevo_nodo.c = nodo_hijo.c[medio:]
            nodo_hijo.c = nodo_hijo.c[0:medio]

    def insert(self, k):
        r = self.root

        if len(r.claves) == self.orden - 1:  # keys are full, so we must split
            s = BTreeNode()
            self.root = s
            s.hijos.insert(0, r)  # former root is now 0th child of new root s
            self._split_child(s, 0)
            self._insert_nonfull(s, k)
        else:
            self._insert_nonfull(r, k)

    def __str__(self):
        r = self.root
        output = ""
        open_set = deque()
        open_set_2 = deque()
        open_set.append(r)

        while open_set:
            subtree_root = open_set.popleft()
            output = output + subtree_root.__str__() + "--"
            for child in subtree_root.hijos:
                open_set_2.append(child)

            if open_set_2 and not open_set:
                open_set = open_set_2
                open_set_2 = deque()
                output = output + '\n'

        return output


if __name__ == '__main__':

    myArbol = BTree(3)
    mynodo = BTreeNode()
    Key = 0

    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad"
    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad, memorización, etc. También puede servir para juegos"
    palabras = "Bienvenidos al creador de palabras aleatorias en español con el puedes crear azar"
    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad, memorización, etc. También puede servir para juegos con niños, por ejemplo, una persona puede generar una palabra sin que otras la vean, hace un dibujo y las otras personas tienen que adivinar cuál es la palabra."
    print("insertando elementos....")

    for pal in palabras.split():
        #print("Insertando palabra [{}]".format(pal))
        myArbol.new_insert(pal.lower())

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
