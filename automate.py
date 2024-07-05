import copy as cp


class automate:
    """
    classe de manipulation des automates
    l'alphabet est l'ensemble des caractères alphabétiques minuscules et "E" pour epsilon, 
    et "O" pour l'automate vide
    """

    def __init__(self, expr="O"):
        """
        construit un automate élémentaire pour une expression régulière expr 
            réduite à un caractère de l'alphabet, ou automate vide si "O"
        identifiant des états = entier de 0 à n-1 pour automate à n états
        état initial = état 0
        """
        
        # alphabet
        alphabet = list("abcdefghijklmnopqrstuvwxyzEO")
        # l'expression doit contenir un et un seul caractère de l'alphabet
        if expr not in alphabet:
            raise ValueError("l'expression doit contenir un et un seul\
                           caractère de l'alphabet " + str(self.alphabet))
        # nombre d'états
        if expr == "O":
            self.n = 0
        elif expr == "E":
            self.n = 1
        else:
            self.n = 2
        # états finals: liste d'états (entiers de 0 à n-1)
        if expr == "O":
            self.final = []
        elif expr == "E":
            self.final = [0]
        else:
            self.final = [1]
        # transitions: dico indicé par (état, caractère) qui donne la liste des états d'arrivée
        self.transition =  {} if (expr in ["O", "E"]) else {(0,expr): [1]}
        # nom de l'automate: obtenu par application des règles de construction
        self.name = "" if expr == "O" else "(" + expr + ")" 

    def __str__(self):
        """affichage de l'automate par fonction print"""
        res = "Automate " + self.name + "\n"
        res += "Nombre d'états " + str(self.n) + "\n"
        res += "Etats finals " + str(self.final) + "\n"
        res += "Transitions:\n"
        for k,v in self.transition.items():    
            res += str(k) + ": " + str(v) + "\n"
        res += "*********************************"
        return res

    def ajoute_transition(self, q0, a, qlist):
        """ajoute la liste de transitions (q0, a, q1) pour tout q1 dans qlist à l'automate"""
        if not isinstance(qlist, list):
            raise TypeError("Erreur de type: ajoute_transition requiert une liste à ajouter")
        if (q0, a) in self.transition:
            self.transition[(q0, a)] = self.transition[(q0, a)] + qlist
        else:
            self.transition.update({(q0, a): qlist})

    ########################################################################################
    #Fait après la remise du projet
    ########################################################################################
    @classmethod
    def cree_automate_parite_a(cls, parite):
        """renvoie l'automate qui reconnait les mots qui ont un nombre de a pair
        (si parite ='pair') ou impair (si parite='impair') et un nombre de b quelconque"""
        a = automate()
        if parite == "pair" :
            a.name = "a_pair"
            a.final = [0]
        elif parite == "impair":
            a.name = "a_impair"
            a.final = [1]
        else :
            raise ValueError("Erreur : la parité doit être 'pair' ou 'impair'")
        a.n = 2
        for i in range(0,2):
            a.ajoute_transition(i, "b", [i])
            a.ajoute_transition(i, "a", [(i+1)%2])
        return a
    ########################################################################################


def concatenation(a1, a2): 
    """Retourne l'automate qui reconnaît la concaténation des 
    langages reconnus par les automates a1 et a2"""
    
    # on copie pour éviter les effets de bord     
    a1 = cp.deepcopy(a1)
    a2 = cp.deepcopy(a2)
    res = automate()
    # les états finals sont ceux de a2 dont les identifiants sont décalés de a1.n
    res.final = [(i + a1.n) for i in a2.final]
    res.name = "(" + a1.name + "." + a2.name + ")"
    # on ajoute les transitions de a1 et a2 en mettant à jour les identifiants
    for k,v in a1.transition.items():
        res.ajoute_transition(*k, v)    
    for k,v in a2.transition.items():
        res.ajoute_transition(k[0] + a1.n, k[1],  [e+a1.n for e in v])
    # on ajoute les epsilon transitions
    for i in a1.final:
        res.ajoute_transition(i, "E", [a1.n])
    # on met à jour la taille de l'automate
    res.n = a1.n + a2.n
    return res


def union(a1, a2):
    """Retourne l'automate qui reconnaît l'union des 
    langages reconnus par les automates a1 et a2""" 
    
    # on copie pour éviter les effets de bord     
    a1 = cp.deepcopy(a1)
    a2 = cp.deepcopy(a2)
    res = automate()
    # les états finals avec le décalage idoine
    res.final = [(i + 1) for i in a1.final] + [(i + 1 + a1.n) for i in a2.final]
    res.name = "(" + a1.name + "+" + a2.name + ")"
    # on ajoute les transitions de a1 et a2 en mettant à jour les identifiants
    for k,v in a1.transition.items():
        res.ajoute_transition(k[0] + 1, k[1],  [e+1 for e in v])
    for k,v in a2.transition.items():
        res.ajoute_transition(k[0] + 1 + a1.n, k[1],  [e+1+a1.n for e in v])   
    # on ajoute les epsilon transition
    res.ajoute_transition(0, "E", [1])
    res.ajoute_transition(0, "E", [1 + a1.n])
    # on met à jour la taille de l'automate
    res.n = a1.n + a2.n + 1
    return res


def etoile(a):
    """Retourne l'automate qui reconnaît l'étoile de Kleene du 
    langage reconnu par l'automate a""" 
    
    # on copie pour éviter les effets de bord     
    a = cp.deepcopy(a)
    res = automate()
    res.final = a.final
    res.transition = a.transition
    # on ajoute les epsilon transition
    for i in res.final:
        res.ajoute_transition(i, "E", [0])
    res.n = a.n
    # on calcule l'automate union avec l'automate epsilon
    res = union(res, automate("E"))
    res.name = a.name + "*"
    return res


def acces_epsilon(a):
    """ retourne la liste pour chaque état des états accessibles par epsilon transitions pour l'automate a
        res[i] est la liste des états accessible pour l'état i
    """
    return [acces_epsilon_recursif(a, i, []) for i in range(a.n)]


def acces_epsilon_recursif(a, i, res_i):
    """ retourne la liste pour l'état i des états accessibles par epsilon transitions pour l'automate a
        res_i est la liste des états accessible pour l'état i
    """
    for v in a.transition.get((i, 'E'), []):
        if v not in res_i :
            res_i.append(v)
            acces_epsilon_recursif(a, v, res_i)
    return res_i


def reconnait(a, mot):
    """ renvoie vrai si le mot mot est reconnu par l'automate a
    """
    return reconnait_recursif(a, [0], mot)


def reconnait_recursif(a, etats, mot):
    """ renvoie vrai si le mot mot est reconnu par l'automate a
    """
    if mot == "":
        for etat in etats :
            if etat in a.final :
                return True
            for accessible_epsilon in acces_epsilon_recursif(a, etat, []):
                if accessible_epsilon in a.final :
                    return True
    else :
        etats = list(set([accessibles_epsilon for etat in etats for accessibles_epsilon in acces_epsilon_recursif(a, etat, [])] + etats))   
        return any(reconnait_recursif(a, v, mot[1:]) for k, v in a.transition.items() if k[1] == mot[0] and k[0] in etats)
    return False


def suppresssion_epsilon(a):
    """ renvoie l'automate a auquel on a supprimé les epsilon-transitions
    """
    a = cp.deepcopy(a)
    transitions = list(a.transition.items())
    accessibles_epsilon = acces_epsilon(a)
    for etat1 in range(a.n):
        for etat2 in accessibles_epsilon[etat1]:
            for k, etats3 in transitions:
                if k[0] == etat2 and k[1] != 'E':
                    a.ajoute_transition(etat1, k[1], etats3)
            if etat2 in a.final and etat1 not in a.final :
                a.final.append(etat1)
    a.final.sort()
    a.transition = {k : v for k, v in a.transition.items() if k[1] != 'E'}
    return a

########################################################################################
#Fait après la remise du projet
########################################################################################
def determiniser(a):
    """ renvoie l'automate a détéminisé
    """
    a = cp.deepcopy(a)
    a_det = automate()
    a_det.name = a.name
    etats = [[0]]
    i = 0
    while etats[i:] != []:
        US = {}
        for etat in etats[i] :
            if etat in a.final and i not in a_det.final:
                a_det.final.append(i)
            for k, v in a.transition.items() :
                if k[0] == etat:
                    if k[1] in US.keys():
                        US[k[1]] = list(set(US[k[1]] + v))
                    else:
                        US[k[1]] = v
        for k, v in US.items():
            if v not in etats :
                etats.append(v)
            a_det.ajoute_transition(i, k, [etats.index(v)])
        i += 1
    a_det.n = len(etats)
    return a_det

def separables(a):
    """ renvoie la matrice matrice de séparabilité de a
    """
    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    tableau = [[True if (q1 in a.final and q2 not in a.final) or (q1 not in a.final and q2 in a.final) else False for q2 in range(a.n)] for q1 in range(a.n)]
    for q1 in range(a.n):
        for q2 in range(a.n):
            if not tableau[q1][q2]:
                for lettre in alphabet:
                    successeur_q1 = a.transition.get((q1, lettre), [])
                    successeur_q2 = a.transition.get((q2, lettre), [])
                    for s1 in successeur_q1:
                        for s2 in successeur_q2:
                            if tableau[s1][s2]:
                                tableau[q1][q2] = True
    return tableau

def minimiser(a):
    """ renvoie l'automate a minimisé
    """
    a = cp.deepcopy(a)
    a_min = automate()
    a_min.name = a.name
    etats = []
    mat_separabilite = separables(a)
    for i in range(a.n):
        etat = []
        for j in range(a.n):
            if mat_separabilite[i][j] == False:
                etat.append(j)
        etat = tuple(sorted(etat))
        if etat not in etats:
            etats.append(etat)
    for i, etat in enumerate(etats):
        for x in etat:
            if x in a.final:
                a_min.final.append(i)
                break
        for k, v in a.transition.items():
            if k[0] == etat[0]:
                for j in range(len(etats)):
                    if v[0] in etats[j]:
                        a_min.ajoute_transition(i, k[1], [j])
    a_min.n = len(etats)
    return a_min
########################################################################################

# TESTS
if __name__ == "__main__":
    # (a)
    a1 = automate("a")
    # (b)
    a2 = automate("b")
    # (ab)
    a3 = concatenation(a1, a2)
    # (a+b)
    a4 = union(a1, a2)
    # a*
    a5 = etoile(a1)
    # a** (pour tester epsilon-transitions accessibilité avec circuit)
    a6 = etoile(a5)
    print(a6)
    print("Epsilon-transitions de a** :")
    print(acces_epsilon(a6))
    print("*********************************")
    # tests de suppression des epsilon-transitions
    print("Test de suppression des epsilon-transitions de a**")
    a7 = suppresssion_epsilon(a6)
    print(a7)
    # tests de reconnaissance
    print("Tests de reconnaissance par a*")
    print(f"aaa : {reconnait(a5, 'aaa')}")
    print(f"aab : {reconnait(a5, 'aab')}")
    print("*********************************")
    print("Tests de reconnaissance par a**")
    print(f"aaa : {reconnait(a6, 'aaa')}")
    print(f"aab : {reconnait(a6, 'aab')}")
    print("*********************************")
    print("Tests de reconnaissance par a** sans epsilon-transitions")
    print(f"aaa : {reconnait(a7, 'aaa')}")
    print(f"aab : {reconnait(a7, 'aab')}")

    ########################################################################################
    #Fait après la remise du projet
    ########################################################################################
    a8 = automate.cree_automate_parite_a("pair")
    a9 = automate.cree_automate_parite_a("impair")
    a10 = concatenation(a8, a9)
    print("*********************************")
    print(a10)
    a11 = suppresssion_epsilon(a10)
    print("Test de suppression des epsilon-transitions de a8.a9")
    print(a11)
    a12 = determiniser(a11)
    print("Test de déterminisattion de a8.a9")
    print(a12)
    a13 = minimiser(a12)
    print("Test de minimisation de a8.a9")
    print(a13)
    ########################################################################################