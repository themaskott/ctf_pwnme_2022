## CRYPTO / Exponential machine


<p align="center">
  <img src="img/consignes.png" />
</p>


Un fichier nous est fourni :
- [chall.py](chall.py)


### Challenge

```python
a = getPrime(512)
x = bytes_to_long(b"PWNME{FAKE_FLAG}")
n = getPrime(512)
print("(a**x) % n =", str(pow(a,x,n)), "\n")
```

Le flag sert de clef pour chiffrer (RSA like) un message connu, il nous faut retrouver cette clef (et donc le flag).

Heureusement un oracle propose d'éffectuer pour nous des opérations : `+ - * // **` sur cette clef et de nous retourner le nouveau message chiffré.


### Solution

L'idée va être de bruteforcer la chiffre par chiffre, en utilisant la division entière par des multiples de 10.

Par exemple si la clef est `2345678901` :
- on va demander à l'oracle de chiffrer le message avec `clef // 100000000 = 2`
- en parallèle on va chiffrer le message `a**i [n]` avec `i` entre 0 et 9 et comparer les chiffrés obtenus pour trouver le premier chiffre de la clef est `2`
- ensuite on recommence avec `clef // 10000000  = 23`
- en parallèle on va chiffrer le message avec `a**(2*10 + i) [N]` avec `i` entre 0 et 9 et comparer les chiffrés obtenus pour trouver le 2e chiffre de la clef : `3`

Et ainsi de suite.

Contrairement à l'énoncé on a pas 30 mais 64 essais (cf boucle `while` du code).

En faisant quelques essais, on trouve que la clef est de longueur `10**93`, en effet `10**94` renvoie `1`.

C'est à dire que `flag // 10**94 = 0`.

Comme on a pas assez de tentatives, on va non pas bruteforcer chiffre par chiffre, mais deux chiffres par deux chiffres.

Jusqu'au dernier, qu'il faudra chercher cette fois avec une addition de `1` en `1` :

Le code : [solve.py](solve.py)

```python
flag = 0
  i = 93
  exp = 10**i

  while(exp!=1):

      exp = 10**i
      if exp < 10:
          exp = 1

      rep = send_bytes(s, '/')

      rep = send_bytes(s, str(exp))

      result = rep.decode().split('\n\n')[0]
      result = int(result.split(' : ')[1])



      for j in range(100):
          tmp = flag * 100 + j
          if pow(a,tmp,n) == result:
              flag = tmp
              print(flag)
              i=i-2
              break

  flag = flag * 10


  # find the last digit
  for j in range(10):

      tmp = flag + j
      if pow(a,tmp,n) == result:
          flag = tmp
          break

  print(long_to_bytes(flag))
```
