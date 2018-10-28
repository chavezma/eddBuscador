import sys
import string
import unicodedata
import bisect
from collections import deque


class BTreeNode(object):

    def __init__(self, es_hoja=False):
        self.es_hoja = es_hoja
        self.claves = []
        self.hijos = []
        self.padre = None

    def __eq__(self, other):
        return self.claves == other.claves and self.hijos == other.hijos and self.padre == other.padre

    def __str__(self):
        if self.es_hoja:
            return "Leaf K:{0}".format(self.claves)
        else:
            return "Internal K:{0}".format(self.claves)


class BTree(object):
    def __init__(self, orden):
        self.root = BTreeNode(es_hoja=True)
        self.orden = orden

    def _path_to(self, k, el_nodo=None, idx_padre=0):
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
                return True, el_nodo, idx_padre
            elif el_nodo.es_hoja:
                # Si recorrio todo el nodo y es una hoja, estoy en el nodo donde deberia ir la clave.
                return False, el_nodo, idx_padre
            else:  # No lo encontre, y no es una hoja, entonces sigo mirando la rama correspondiente
                return self._path_to(k, el_nodo.hijos[idx], idx)
        else:  # no node provided, search root of tree
            return self._path_to(k, self.root, 0)

    def insert(self, k):
        existe, el_nodo, idx = self._path_to(k)

        if existe:
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

            self._split_hoja(el_padre, idx, k)

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

        # Buscamos el indice del nodo que corresponde al hijo.
        idx_h = 0
        for child in el_padre.hijos:
            if child != rama:
                idx_h += 1
            else:
                break

        self._split_interno(el_padre, idx_h)

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
            # Re-armo los hijos del hermando "derecho"
            nuevo_nodo.hijos = nodo_hijo.hijos[medio+1:]
            for hijo in nuevo_nodo.hijos:
                hijo.padre = nuevo_nodo
            # Re-armo los hijos del hermano "izquierdo" el que "se partio"
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

    def search(self, key, el_nodo=None):
        if isinstance(el_nodo, BTreeNode):
            i = 0
            while i < len(el_nodo.claves) and key > el_nodo.claves[i]:  # look for index of k
                i += 1
            if i < len(el_nodo.claves) and key == el_nodo.claves[i]:  # found exact match
                return el_nodo, i
            elif el_nodo.es_hoja:  # no match in keys, and is leaf ==> no match exists
                return None, 0
            else:  # search children
                return self.search(key, el_nodo.hijos[i])
        else:  # no node provided, search root of tree
            return self.search(key, self.root)

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


def normalizar(palabra):
    if sys.hexversion >= 0x3000000:
        # On Python >= 3.0.0
        output = remove_diacritic(palabra).decode()
    else:
        # On Python < 3.0.0
        output = remove_diacritic(unicode(palabra, 'ISO-8859-1'))

    return output.translate(str.maketrans('', '', string.punctuation))


def remove_diacritic(input):
    return unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')


if __name__ == '__main__':
    #print("".join(reversed(balloon)))
    myArbol = BTree(3)
    resNodo = None
    resIdx = 0

    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad"
    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad, memorización, etc. También puede servir para juegos"
    palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad, memorización, etc. También puede servir para juegos con niños, por ejemplo, una persona puede generar una palabra sin que otras la vean, hace un dibujo y las otras personas tienen que adivinar cuál es la palabra."
    #palabras = "Bienvenidos al creador de palabras aleatorias en español, con él puedes crear palabras al azar para ejercicios de creatividad, memorización, etc. También puede servir para juegos con niños, por ejemplo, una persona puede generar una palabra sin que otras la vean, hace un dibujo y las otras personas tienen que adivinar cuál es la palabra."

    for pal in palabras.split():
        myArbol.insert( normalizar(pal.lower()) )

    print(myArbol)

    resNodo, resIdx = myArbol.search("aleatorias")
    print(resNodo)
    print(resIdx)

    resNodo, resIdx = myArbol.search("aleator")
    print(resNodo)
    print(resIdx)
