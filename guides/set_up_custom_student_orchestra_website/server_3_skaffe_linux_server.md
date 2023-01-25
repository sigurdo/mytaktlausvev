# Fullstendig vegvisar for å setje opp eigen studentorchestervev

## Skaffe Linux-server

Du må nå skaffe tilgjenge til ein virtuell eller fysisk Linux-server du kan hoste veven din frå. Dette kan gjerast med mange ulike distroar hos mange ulike hosting-tilbydarar. Viss du ikkje veit korleis du gjer det på eiga hand anbefaler eg å følge oppsettet beskrive under.

### VULTR Docker Ubuntu oppsett

VULTR er ein fin plattform for server-hosting der du alltid betalar det samme per time, og ikkje må binde deg til eit år av gongen for å få det billig. Gå til [vultr.com](https://www.vultr.com/) og opprett ein ny konto og legg like gjerne inn betalingsinfo før du går vidare. Deretter kan du gå til https://my.vultr.com/deploy/ og velge følgjande ny server-konfigurasjon:

- Choose Server: Cloud Compute
- CPU & Storage Technology: Regular Performance er sannsynlegvis bra nok, men du kjem nok til å merke at veven er litt raskare med High Performance. High Frequency trenger du ikkje.
- Server Location: Velg ein i nærleiken av der studentorchesteret ditt held til.
- Server Image: Marketplace Apps > Docker > Ubuntu 20.04 x64
- Server Size: 25 GB eller 50 GB. Du kan godt starte lågt, sidan du enkelt kan oppgradere, men ikkje degradere i ettertid.
- Add Auto Backups: On
- Additional Features: Enable IPv6
- SSH Keys: Ingenting
- Server Hostname & Label: Her kan du til dømes bruket navnet på studentorchesteret ditt, men skrive kun med bokstavar frå A til Z og utan mellomrom.

Dette skal koste mellom $6 og $14 per månad, avhengig av kva for spesifikasjonar du valgte. No kan du gå til [instans-oversikta di](https://my.vultr.com/) og trykke deg inn på instansen du akkurat oppretta. Den kjem nok til å bruke eitt eller to minutt på å starte, og så kan du logge deg inn med brukarnamnet, IP-addressa og passordet som står der.

```
ssh <brukarnamn>@<IP-addresse>
```

[Forrige side](2_azure_eller_server.md) | [Neste side](server_4_serveroppsett.md)
