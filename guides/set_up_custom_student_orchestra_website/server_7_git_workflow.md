# Fullstendig vegvisar for å setje opp eigen studentorchestervev

## Git-arbeidsflyt

Gratulerer, du skal nå i teorien vere ferdig med å setje opp sjølve studentorchestervevsida di!⭐🎉🪩 Nå trenger du egentleg ikkje følgje denne guiden noko vidare, men det vert sterkt anbefala. Herifrå kjem guiden til å i mykje større grad anta at du har litt peiling på git, terminalbruk og programvareutvikling generelt.

Det fyrste du bør gjere no er å committe og pushe konfigurasjons-fila di saman med logoen til ditt eiget git-repo.

```
git add .
git commit -m "Setup website"
git remote rename origin mytaktlausvev
git remote add origin <URL til remote-repoet ditt>
git push -u origin main
```

Repoet ditt har nå 2 remotes, `origin` (din eigen) og `mytaktlausvev` (det offisielle mytaktlausvev-repoet). Det gjer at du enkelt kan ta vare på dine egne endringar og samtidig pulle nye versjonar av MyTaktlausvev når du vil. For å pulle/merge inn den siste versjonen av MyTaktlausvev kan du gjere følgande:

```
git fetch mytaktlausvev
git merge mytaktlausvev/main
git submodule update --init --recursive
```

[Forrige side](server_6_vevoppsett.md) | [Neste side](server_8_backup.md)
