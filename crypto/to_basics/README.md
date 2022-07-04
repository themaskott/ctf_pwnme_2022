## CRYPTO / To basics


<p align="center">
  <img src="img/consignes.png" />
</p>


Deux fichiers nous sont fournis :
- [encrypt.py](encrypt.py)
- [flag-encrypted.py](flag-encrypted.py)


### Solve

Le problème de cet algo est le `SECRET = choice(digits) * len(FLAG)` qui voudrait générer une clef random, mais `choice(digits)` ne retourne qu'une valeur parmis `digits` soit 0 à 9.

La suite n'est qu'un `xor`

Il suffit donc de bruteforcer (avec le petit décalage qui convient):

```python
from string import digits

flag = [97,103,129,127,120,79,109,9,75,81,120,126,17,79,14,129,126,19,113,133,87,21,119,29,144,26,121,103]


for d in digits:
	i = 0
	for c in flag:
		print( chr( ((c-i)^ord(d))), end="" )
		i+=1
	print()
```

`PWNME{V3ry_B4s1C_3nCr1P7I0n}`
