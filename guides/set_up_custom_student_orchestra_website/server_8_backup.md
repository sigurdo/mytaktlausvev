# Fullstendig vegvisar for å setje opp eigen studentorchestervev

## Backup

Så fort du byrjar bruke veven aktivt i orchesteret, bør du ta backups av databasen frå tid til annan. Det kan gjerast relativt enkelt med følgande kommando:

```
./prod.py store-backup <filnamn>.sql <database-konteiner-namn>
```

Namnet på database-konteineren kan du finne med

```
docker container ls
```

Det er vanlegvis `website_build_db_1`.

For å laste inn ein backup kan du bruke

```
./prod.py restore-backup <filnamn>.sql <database-konteiner-namn>
```

Merk at dette berre tar backup av databasen. For å ta backup av bildar og andre filar som har vorte lasta opp til veven må du ta backup av `~/media_files`. Dette kan du gjere med

```
tar -C ~/ -czf media_files_backup.tar.gz media_files
```

, og laste inn ein backup med

```
tar -C ~/ -xzf media_files_backup.tar.gz
```

Du burde ikkje berre lagre backups på serveren. Frå tid til annan bør du også lagre backups på din eigen datamaskin, eller ein annan server. Du kan også gjerne sette opp ein cronjob som lagrar backups på serveren fast ein gong om dagen, og så kan du dobbeltlagre dei på PCen din litt sjeldnare.

[Forrige side](server_7_git_workflow.md)
