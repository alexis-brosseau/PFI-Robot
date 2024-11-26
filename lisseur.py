# Fait par Alexis Brosseau
# 12 sept. 2024

class Lisseur:
    
    def __init__(self, fenetre):
        self.data = []
        self.fenetre = fenetre
        self.moyenne = 0

    def ajouter(self, valeur, keep_minmax = True):
        
        if (len(self.data) > self.fenetre):
            del self.data[0]
        
        self.data.append(valeur)
        
        # retirer min et max
        copy = self.data.copy()
        if (len(copy) > 2 and not keep_minmax):
            copy.remove(min(copy))
            copy.remove(max(copy))
        
        # moyenne
        self.moyenne = sum(copy) / len(copy)