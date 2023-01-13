# Fullstendig vegvisar for å setje opp eigen studentorchestervev

## Setje opp veven

Det er på tide å setje opp sjølve vevsida, start med å klone MyTaktlausvev-kildekoden:

```
git clone --recurse-submodules https://github.com/sigurdo/mytaktlausvev.git
cd mytaktlausvev
```

Nå byrjar moroa, det er på tide å konfigurere utsjånaden til veven. Det første du må gjere er å overføre logoen til orchesteret ditt til serveren (denne kommandoen skal du altså kjøre på PCen der du har logoen):

```
scp logo.png <brukarnamn>@<IP-addresse>:~/mytaktlausvev/static_files/logo.png
```

Så kan du starte MyTaktlausvev-trollmannen og fylle ut det han spør om (denne kommandoen kjører du på serveren):

```
python3 -m pip install -r requirements.txt
./wizard.py
```

Når du er ferdig har trollmannen oppretta ein konfigurasjonsfil (`config.toml`) og ein server-secrets-fil (`server_secrets.toml`). Desse kan du endre sjøl i etterkant hvis du vil endre på ting. Ikkje endre på server-tekniske ting viss du ikkje veit kva du gjer. Når du har endra innstillingane må du bygge og starte opp vevsida på nytt. Dette gjerast enkelt med kommandoen:

```
./prod.py rebuild
```

Hvis du vil stoppe veven kan du kjøre

```
./prod.py stop
```

, og for å starte den opp att kan du kjøre

```
./prod.py start
```

[Forrige side](server_5_domene.md) | [Neste side](server_7_git_workflow.md)
