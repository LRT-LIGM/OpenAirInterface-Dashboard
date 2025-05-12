# Installation Process

## Become a Sudoer

To give a user sudo privileges, run :

```bash
sudo usermod -aG sudo <username>
```
Replace <username> with the actual name of the user.


To check if the user has sudo access, run :

```bash
sudo whoami
```

If the command returns root, it means the user has sudo privileges.
