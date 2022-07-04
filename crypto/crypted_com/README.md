## CRYPTO / Encrypted Communication


<p align="center">
  <img src="img/consignes.png" />
</p>


Deux fichiers nous sont fournis :
- [chall.py](chall.py)
- [output.txt](output.txt)


### Solve


Problème :

```python
p, q, s = getPrime(2048), getPrime(2048), getPrime(2048)
n1 = p * q
n2 = s * p
```

Nous avons deux messages chiffrés avec deux clefs publiques `(e,n1)` et `(e,n2)` différentes .... En revanche `n1` et `n2` partagent un entier premier générateur commun : `p`.

Il est du coup assez trivial de le retrouver : `p = GCD(n1,n2)` et de là reconstruire les deux clefs privées permettant de déchiffrer les deux morceaux du flag.
